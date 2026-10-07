from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.db.continuity_models import Child, MigrationRecord, ServiceContinuityRecord
from app.db.models import User
from app.schemas.continuity import ContinuitySummary, ContinuityUpdate, ServiceContinuityOut
from app.services.continuity import child_continuity_summary, refresh_child_continuity
from app.services.continuity_access import ensure_child_access

router = APIRouter(tags=['service continuity'])
SERVICE_ROLES = {
    'EDUCATION': ('CITIZEN', 'SCHOOL', 'NGO_WORKER', 'ADMIN'),
    'HEALTHCARE': ('CITIZEN', 'HEALTHCARE', 'NGO_WORKER', 'ADMIN'),
    'NUTRITION': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
    'PROTECTION': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
    'WELLBEING': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
    'INCLUSION': ('CITIZEN', 'NGO_WORKER', 'ADMIN'),
}


@router.get('/continuity/summary')
def get_aggregate_continuity_summary(
    current_user: User = Depends(require_role('GOVERNMENT', 'ADMIN')),
    db: Session = Depends(get_db),
) -> dict:
    latest_migration_id = (
        select(MigrationRecord.id)
        .where(MigrationRecord.family_id == Child.family_id)
        .order_by(MigrationRecord.migration_date.desc(), MigrationRecord.created_at.desc())
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
    ensure_child_access(db, current_user, record.child_id, SERVICE_ROLES[record.service_type])
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record