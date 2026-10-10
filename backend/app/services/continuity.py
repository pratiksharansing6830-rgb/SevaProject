from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.db.continuity_models import (
    Child,
    ChildProtectionRecord,
    EducationRecord,
    FollowUpAction,
    HealthcareContinuity,
    InclusionRecord,
    MigrationRecord,
    NutritionRecord,
    ServiceContinuityRecord,
    WellBeingRecord,
)

SERVICE_ROLES = {
    'EDUCATION': 'SCHOOL',
    'HEALTHCARE': 'HEALTHCARE',
    'NUTRITION': 'NGO_WORKER',
    'PROTECTION': 'NGO_WORKER',
    'WELLBEING': 'NGO_WORKER',
    'INCLUSION': 'NGO_WORKER',
}


def _service_reason(service_type: str, service_status: str) -> str:
    if service_status == 'SUPPORT_NOT_REQUIRED':
        return f'{service_type.replace("_", " ").title()} support was confirmed as not required.'
    reasons = {
        'EDUCATION': {
            'CONNECTED': 'Education continuity is connected and confirmed.',
            'FOLLOW_UP_REQUIRED': 'Education enrollment or transfer requires follow-up.',
            'REVIEW_REQUIRED': 'Education continuity needs review because enrollment or transfer is unresolved.',
            'PENDING': 'Education enrollment information has not been confirmed.',
        },
        'HEALTHCARE': {
            'CONNECTED': 'Healthcare continuity is connected and confirmed.',
            'FOLLOW_UP_REQUIRED': 'Healthcare continuity requires follow-up with the health provider.',
            'REVIEW_REQUIRED': 'Healthcare continuity needs review.',
            'PENDING': 'Healthcare support information has not been confirmed.',
        },
        'NUTRITION': {
            'CONNECTED': 'Nutrition support is connected and confirmed.',
            'FOLLOW_UP_REQUIRED': 'Nutrition support needs follow-up because the connection is not confirmed.',
            'REVIEW_REQUIRED': 'Nutrition support needs review.',
            'PENDING': 'Nutrition support information has not been confirmed.',
        },
        'PROTECTION': {
            'CONNECTED': 'Protection support is connected and confirmed.',
            'FOLLOW_UP_REQUIRED': 'Protection support requires follow-up.',
            'REVIEW_REQUIRED': 'Protection needs a safeguarding review.',
            'PENDING': 'Protection support has not yet been assessed or confirmed.',
        },
        'WELLBEING': {
            'CONNECTED': 'Wellbeing support is connected and confirmed.',
            'FOLLOW_UP_REQUIRED': 'Wellbeing support requires follow-up.',
            'REVIEW_REQUIRED': 'Wellbeing support requires review.',
            'PENDING': 'Wellbeing support information has not been confirmed.',
        },
        'INCLUSION': {
            'CONNECTED': 'Inclusion support is connected and confirmed.',
            'FOLLOW_UP_REQUIRED': 'The required inclusion adjustment needs follow-up.',
            'REVIEW_REQUIRED': 'Inclusion support needs review.',
            'PENDING': 'Inclusion support requirement has not been confirmed.',
        },
    }
    return reasons[service_type][service_status]


def _service_status(child: Child, service_type: str) -> str:
    if service_type == 'EDUCATION':
        record = child.education
        if not record:
            return 'PENDING'
        if record.transfer_status in ('PENDING', 'NOT_STARTED') or record.enrollment_status in ('PENDING', 'NOT_ENROLLED'):
            return 'FOLLOW_UP_REQUIRED'
        if record.enrollment_status == 'ENROLLED' and record.transfer_status in ('COMPLETED', 'NOT_REQUIRED'):
            return 'CONNECTED'
        return 'PENDING'
    if service_type == 'HEALTHCARE':
        return _normalize_service_status(child.healthcare.continuity_status) if child.healthcare else 'PENDING'
    if service_type == 'NUTRITION':
        return _normalize_service_status(child.nutrition.service_status) if child.nutrition else 'PENDING'
    if service_type == 'PROTECTION':
        record: ChildProtectionRecord | None = child.protection
        if not record:
            return 'PENDING'
        if record.protection_status == 'REVIEW_REQUIRED':
            return 'REVIEW_REQUIRED'
        if record.followup_required:
            return 'FOLLOW_UP_REQUIRED'
        if record.protection_status == 'FOLLOW_UP_RECOMMENDED':
            return 'FOLLOW_UP_REQUIRED'
        if record.protection_status == 'SUPPORT_CONNECTED':
            return 'CONNECTED'
        if record.protection_status == 'NO_ACTION_RECORDED':
            return 'PENDING'
        return 'REVIEW_REQUIRED'
    if service_type == 'WELLBEING':
        return _normalize_service_status(child.wellbeing.support_status) if child.wellbeing else 'PENDING'
    record: InclusionRecord | None = child.inclusion
    if not record:
        return 'PENDING'
    if record.requirement_present is False:
        return 'SUPPORT_NOT_REQUIRED'
    if record.requirement_present is None:
        return 'PENDING'
    return _normalize_service_status(record.support_status)


def _normalize_service_status(status: str) -> str:
    if status == 'CONNECTED':
        return 'CONNECTED'
    if status in ('FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE'):
        return 'FOLLOW_UP_REQUIRED'
    return 'PENDING'


def _source_record(child: Child, service_type: str):
    return {
        'EDUCATION': child.education,
        'HEALTHCARE': child.healthcare,
        'NUTRITION': child.nutrition,
        'PROTECTION': child.protection,
        'WELLBEING': child.wellbeing,
        'INCLUSION': child.inclusion,
    }[service_type]


def _is_after(value: datetime | None, reference: datetime) -> bool:
    if value is None:
        return False
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    return value > reference


def _confirmed_outcome(record: ServiceContinuityRecord) -> bool:
    return (
        record.status in ('CONNECTED', 'SUPPORT_NOT_REQUIRED')
        and record.outcome_confirmed_by_user_id is not None
        and record.outcome_confirmed_at is not None
        and record.confirmation_method is not None
    )


def current_family_migration(db: Session, family_id: UUID) -> MigrationRecord | None:
    status_order = case(
        (MigrationRecord.status == 'ACTIVE', 0),
        (MigrationRecord.status == 'COMPLETED', 1),
        else_=2,
    )
    return (
        db.query(MigrationRecord)
        .filter(MigrationRecord.family_id == family_id)
        .order_by(
            status_order,
            MigrationRecord.migration_date.desc(),
            MigrationRecord.created_at.desc(),
        )
        .first()
    )


def unresolved_continuity_statuses(
    db: Session,
    child: Child,
    migration: MigrationRecord | None,
) -> dict[str, str]:
    query = db.query(ServiceContinuityRecord).filter(ServiceContinuityRecord.child_id == child.id)
    if migration:
        query = query.filter(ServiceContinuityRecord.migration_id == migration.id)
    else:
        query = query.filter(ServiceContinuityRecord.migration_id.is_(None))
    return {
        record.service_type: record.status
        for record in query.all()
        if record.status in ('FOLLOW_UP_REQUIRED', 'REVIEW_REQUIRED')
    }


def refresh_child_continuity(
    db: Session,
    child: Child,
    migration: MigrationRecord | None = None,
    inherited_statuses: dict[str, str] | None = None,
) -> list[ServiceContinuityRecord]:
    migration = migration or current_family_migration(db, child.family_id)
    inherited_statuses = inherited_statuses or {}
    service_types = ('EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION')
    records: list[ServiceContinuityRecord] = []
    for service_type in service_types:
        query = db.query(ServiceContinuityRecord).filter(
            ServiceContinuityRecord.child_id == child.id,
            ServiceContinuityRecord.service_type == service_type,
        )
        if migration:
            query = query.filter(ServiceContinuityRecord.migration_id == migration.id)
        else:
            query = query.filter(ServiceContinuityRecord.migration_id.is_(None))
        record = query.first()
        candidate_status = _service_status(child, service_type)
        carried_status = inherited_statuses.get(service_type)
        if carried_status == 'REVIEW_REQUIRED' or (
            carried_status == 'FOLLOW_UP_REQUIRED' and candidate_status == 'PENDING'
        ):
            candidate_status = carried_status
        if record and _confirmed_outcome(record):
            source_record = _source_record(child, service_type)
            source_changed = _is_after(source_record.updated_at if source_record else None, record.outcome_confirmed_at)
            protection_review = service_type == 'PROTECTION' and candidate_status == 'REVIEW_REQUIRED'
            if protection_review or (source_changed and candidate_status != record.status):
                record.outcome_confirmed_by_user_id = None
                record.outcome_confirmed_at = None
                record.confirmation_method = None
                record.supporting_reference = None
            else:
                candidate_status = record.status
        elif record and record.status == 'REVIEW_REQUIRED':
            candidate_status = 'REVIEW_REQUIRED'
        elif record and record.status == 'FOLLOW_UP_REQUIRED' and candidate_status == 'PENDING':
            candidate_status = 'FOLLOW_UP_REQUIRED'
        service_status = candidate_status
        if service_status in ('CONNECTED', 'SUPPORT_NOT_REQUIRED') and not (record and _confirmed_outcome(record)):
            service_status = 'PENDING'
        action_required = service_status not in ('CONNECTED', 'SUPPORT_NOT_REQUIRED')
        reason = _service_reason(service_type, service_status)
        if not record:
            record = ServiceContinuityRecord(
                child_id=child.id,
                migration_id=migration.id if migration else None,
                service_type=service_type,
                status=service_status,
                reason=reason,
                action_required=action_required,
                assigned_role=SERVICE_ROLES[service_type] if action_required else None,
                due_date=date.today() + timedelta(days=7) if action_required else None,
            )
            db.add(record)
            db.flush()
        else:
            record.status = service_status
            record.reason = reason
            record.action_required = action_required
            record.assigned_role = SERVICE_ROLES[service_type] if action_required else None
            record.due_date = (record.due_date or date.today() + timedelta(days=7)) if action_required else None
            if not _confirmed_outcome(record):
                record.outcome_confirmed_by_user_id = None
                record.outcome_confirmed_at = None
                record.confirmation_method = None
                record.supporting_reference = None

        if action_required:
            pending_action = (
                db.query(FollowUpAction)
                .filter(
                    FollowUpAction.service_continuity_id == record.id,
                    FollowUpAction.status.in_(('OPEN', 'IN_PROGRESS')),
                )
                .first()
            )
            if not pending_action:
                db.add(
                    FollowUpAction(
                        family_id=child.family_id,
                        child_id=child.id,
                        service_continuity_id=record.id,
                        title=f'{service_type.replace("_", " ").title()} continuity follow-up',
                        description=record.reason or 'Review this service connection with the family and record the outcome.',
                        status='OPEN',
                        priority='MEDIUM',
                        due_date=record.due_date or date.today() + timedelta(days=7),
                        assigned_role=SERVICE_ROLES[service_type],
                    )
                )
        records.append(record)
    db.flush()
    return records


def child_continuity_summary(db: Session, child: Child) -> dict:
    migration = current_family_migration(db, child.family_id)
    records = refresh_child_continuity(db, child, migration)
    statuses = {record.status for record in records}
    overall = 'REVIEW_REQUIRED' if 'REVIEW_REQUIRED' in statuses else (
        'FOLLOW_UP_REQUIRED'
        if statuses.intersection({'PENDING', 'FOLLOW_UP_REQUIRED'})
        else 'SUPPORT_NOT_REQUIRED' if statuses == {'SUPPORT_NOT_REQUIRED'} else 'CONNECTED'
    )
    return {
        'child_id': child.id,
        'child_name': f'{child.first_name} {child.last_name}',
        'overall_status': overall,
        'services': records,
        'follow_up_count': sum(record.action_required for record in records),
    }