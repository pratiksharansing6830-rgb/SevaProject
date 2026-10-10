from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, case, exists, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.api.deps import get_current_user, get_db, require_role
from app.db.continuity_models import Child, Family, FollowUpAction, MigrationRecord, ServiceContinuityRecord
from app.db.models import User
from app.schemas.continuity import ContinuitySummary, ContinuityUpdate, ServiceContinuityOut
from app.services.continuity import (
    SERVICE_ROLES as SERVICE_ASSIGNED_ROLES,
    _service_status,
    _service_reason,
    child_continuity_summary,
    refresh_child_continuity,
)
from app.services.continuity_access import ensure_child_access

router = APIRouter(tags=['service continuity'])
GOVERNMENT_GEO_SUPPRESSION_THRESHOLD = 5
CONTINUITY_SERVICE_TYPES = ('EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION')
UNRESOLVED_STATUSES = ('PENDING', 'FOLLOW_UP_REQUIRED', 'REVIEW_REQUIRED')
SERVICE_ROLES = {
    'EDUCATION': ('CITIZEN', 'SCHOOL', 'NGO_WORKER', 'ADMIN'),
    'HEALTHCARE': ('CITIZEN', 'HEALTHCARE', 'NGO_WORKER', 'ADMIN'),
    'NUTRITION': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
    'PROTECTION': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
    'WELLBEING': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
    'INCLUSION': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
}


@router.get('/government/dashboard')
def get_government_dashboard(
    current_user: User = Depends(require_role('GOVERNMENT', 'ADMIN')),
    db: Session = Depends(get_db),
) -> dict:
    migration_status_order = case(
        (MigrationRecord.status == 'ACTIVE', 0),
        (MigrationRecord.status == 'COMPLETED', 1),
        else_=2,
    )
    latest_migration_id = (
        select(MigrationRecord.id)
        .where(MigrationRecord.family_id == Child.family_id)
        .order_by(
            migration_status_order,
            MigrationRecord.migration_date.desc(),
            MigrationRecord.created_at.desc(),
        )
        .limit(1)
        .correlate(Child)
        .scalar_subquery()
    )
    no_migration = ~exists(select(MigrationRecord.id).where(MigrationRecord.family_id == Child.family_id))
    current_records = (
        db.query(ServiceContinuityRecord)
        .join(Child, Child.id == ServiceContinuityRecord.child_id)
        .join(Family, Family.id == Child.family_id)
        .filter(or_(
            ServiceContinuityRecord.migration_id == latest_migration_id,
            and_(ServiceContinuityRecord.migration_id.is_(None), no_migration),
        ))
        .filter(~Family.family_reference_id.like('DEMO-%'))
    )

    migration_counts = dict(
        db.query(MigrationRecord.status, func.count(MigrationRecord.id))
        .join(Family, Family.id == MigrationRecord.family_id)
        .filter(~Family.family_reference_id.like('DEMO-%'))
        .group_by(MigrationRecord.status)
        .all()
    )
    service_status_counts = (
        current_records.with_entities(
            ServiceContinuityRecord.service_type,
            ServiceContinuityRecord.status,
            func.count(ServiceContinuityRecord.id),
        )
        .group_by(ServiceContinuityRecord.service_type, ServiceContinuityRecord.status)
        .all()
    )
    unresolved_by_type: dict[str, dict[str, int]] = {
        service_type: {status: 0 for status in UNRESOLVED_STATUSES}
        for service_type in CONTINUITY_SERVICE_TYPES
    }
    for service_type, service_status, count in service_status_counts:
        if service_status in UNRESOLVED_STATUSES:
            unresolved_by_type[service_type][service_status] = count

    today = date.today()
    active_followups = (
        db.query(FollowUpAction)
        .join(Family, Family.id == FollowUpAction.family_id)
        .filter(
            FollowUpAction.status.in_(('OPEN', 'IN_PROGRESS')),
            ~Family.family_reference_id.like('DEMO-%'),
        )
    )
    due_today = active_followups.filter(FollowUpAction.due_date == today).count()
    overdue = active_followups.filter(FollowUpAction.due_date < today).count()

    current_migration = aliased(MigrationRecord)
    destination_district = func.nullif(func.trim(func.coalesce(current_migration.to_district, Family.current_district)), '')
    service_gaps = (
        current_records.outerjoin(current_migration, current_migration.id == latest_migration_id)
        .with_entities(
            destination_district.label('district'),
            ServiceContinuityRecord.service_type,
            func.count(ServiceContinuityRecord.id).label('need_count'),
            func.count(func.distinct(ServiceContinuityRecord.child_id)).label('child_count'),
        )
        .filter(
            ServiceContinuityRecord.status.in_(UNRESOLVED_STATUSES),
            destination_district.isnot(None),
        )
        .group_by(destination_district, ServiceContinuityRecord.service_type)
        .having(func.count(func.distinct(Family.id)) >= GOVERNMENT_GEO_SUPPRESSION_THRESHOLD)
        .order_by(destination_district, ServiceContinuityRecord.service_type)
        .all()
    )

    six_month_window_start = date(today.year, today.month, 1)
    for _ in range(5):
        six_month_window_start = date(
            six_month_window_start.year - (six_month_window_start.month == 1),
            12 if six_month_window_start.month == 1 else six_month_window_start.month - 1,
            1,
        )
    migration_year = func.extract('year', MigrationRecord.migration_date)
    migration_month = func.extract('month', MigrationRecord.migration_date)
    trend_rows = (
        db.query(
            migration_year.label('year'),
            migration_month.label('month'),
            func.count(MigrationRecord.id).label('migration_count'),
            func.count(func.distinct(MigrationRecord.family_id)).label('family_count'),
        )
        .join(Family, Family.id == MigrationRecord.family_id)
        .filter(
            MigrationRecord.migration_date >= six_month_window_start,
            MigrationRecord.migration_date <= today,
            MigrationRecord.status.in_(('ACTIVE', 'COMPLETED')),
            ~Family.family_reference_id.like('DEMO-%'),
        )
        .group_by(migration_year, migration_month)
        .order_by(migration_year, migration_month)
        .all()
    )

    return {
        'as_of': today.isoformat(),
        'privacy': {
            'aggregate_only': True,
            'geographic_suppression_threshold': GOVERNMENT_GEO_SUPPRESSION_THRESHOLD,
            'small_geographic_groups_suppressed': True,
        },
        'profile_counts': {
            'family_count': db.query(func.count(Family.id)).filter(~Family.family_reference_id.like('DEMO-%')).scalar() or 0,
            'child_count': (
                db.query(func.count(Child.id))
                .join(Family, Family.id == Child.family_id)
                .filter(~Family.family_reference_id.like('DEMO-%'))
                .scalar()
                or 0
            ),
        },
        'migration_counts': {
            status: migration_counts.get(status, 0)
            for status in ('PLANNED', 'ACTIVE', 'COMPLETED')
        },
        'unresolved_needs_by_service': [
            {
                'service_type': service_type,
                'pending': counts['PENDING'],
                'follow_up_required': counts['FOLLOW_UP_REQUIRED'],
                'review_required': counts['REVIEW_REQUIRED'],
                'total': sum(counts.values()),
            }
            for service_type, counts in unresolved_by_type.items()
        ],
        'followups': {
            'open_or_in_progress': active_followups.count(),
            'due_today': due_today,
            'overdue': overdue,
        },
        'destination_service_gaps': [
            {
                'district': district,
                'service_type': service_type,
                'unresolved_need_count': need_count,
                'affected_child_count': child_count,
            }
            for district, service_type, need_count, child_count in service_gaps
        ],
        'migration_trend': [
            {
                'month': f'{int(year):04d}-{int(month):02d}',
                'migration_count': migration_count,
                'family_count': family_count,
            }
            for year, month, migration_count, family_count in trend_rows
            if family_count >= GOVERNMENT_GEO_SUPPRESSION_THRESHOLD
        ],
    }


@router.get('/continuity/summary')
def get_aggregate_continuity_summary(
    current_user: User = Depends(require_role('GOVERNMENT', 'ADMIN')),
    db: Session = Depends(get_db),
) -> dict:
    migration_status_order = case(
        (MigrationRecord.status == 'ACTIVE', 0),
        (MigrationRecord.status == 'COMPLETED', 1),
        else_=2,
    )
    latest_migration_id = (
        select(MigrationRecord.id)
        .where(MigrationRecord.family_id == Child.family_id)
        .order_by(
            migration_status_order,
            MigrationRecord.migration_date.desc(),
            MigrationRecord.created_at.desc(),
        )
        .limit(1)
        .correlate(Child)
        .scalar_subquery()
    )
    no_migration = ~exists(select(MigrationRecord.id).where(MigrationRecord.family_id == Child.family_id))
    rows = (
        db.query(
            ServiceContinuityRecord.service_type,
            ServiceContinuityRecord.status,
            func.count(ServiceContinuityRecord.id),
        )
        .join(Child, Child.id == ServiceContinuityRecord.child_id)
        .filter(or_(
            ServiceContinuityRecord.migration_id == latest_migration_id,
            and_(ServiceContinuityRecord.migration_id.is_(None), no_migration),
        ))
        .group_by(ServiceContinuityRecord.service_type, ServiceContinuityRecord.status)
        .all()
    )
    return {
        'child_count': db.query(func.count(Child.id)).scalar() or 0,
        'service_status_counts': [
            {'service_type': service_type, 'status': service_status, 'count': count}
            for service_type, service_status, count in rows
        ],
    }


@router.get('/children/{child_id}/continuity', response_model=ContinuitySummary)
def get_continuity(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    summary = child_continuity_summary(db, child)
    db.commit()
    return summary


@router.post('/children/{child_id}/continuity/check', response_model=list[ServiceContinuityOut])
def check_continuity(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    records = refresh_child_continuity(db, child)
    db.commit()
    return records


@router.put('/continuity/{record_id}', response_model=ServiceContinuityOut)
def update_continuity(
    record_id: UUID,
    payload: ContinuityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.get(ServiceContinuityRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail='Continuity record not found.')
    child = ensure_child_access(db, current_user, record.child_id, SERVICE_ROLES[record.service_type])
    if (
        payload.status in ('CONNECTED', 'SUPPORT_NOT_REQUIRED')
        and record.service_type == 'PROTECTION'
        and _service_status(child, 'PROTECTION') == 'REVIEW_REQUIRED'
    ):
        raise HTTPException(status_code=409, detail='Protection review must be resolved before confirming a connection.')
    record.status = payload.status
    record.action_required = payload.status not in ('CONNECTED', 'SUPPORT_NOT_REQUIRED')
    record.assigned_role = SERVICE_ASSIGNED_ROLES[record.service_type] if record.action_required else None
    record.due_date = (payload.due_date or record.due_date) if record.action_required else None
    if 'notes' in payload.model_fields_set:
        record.notes = payload.notes
    record.reason = _service_reason(record.service_type, record.status)
    if record.action_required:
        record.outcome_confirmed_by_user_id = None
        record.outcome_confirmed_at = None
        record.confirmation_method = None
        record.supporting_reference = None
    else:
        record.outcome_confirmed_by_user_id = current_user.id
        record.outcome_confirmed_at = datetime.now(timezone.utc)
        record.confirmation_method = payload.confirmation_method
        record.supporting_reference = payload.supporting_reference
        for followup in record.followups:
            if followup.status in ('OPEN', 'IN_PROGRESS'):
                followup.status = 'COMPLETED'
    db.commit()
    db.refresh(record)
    return record