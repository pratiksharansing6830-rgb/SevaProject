from datetime import date, timedelta
from uuid import UUID

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


def _service_status(child: Child, service_type: str) -> str:
    if service_type == 'EDUCATION':
        record = child.education
        if not record:
            return 'PENDING'
        if record.transfer_status == 'PENDING' or record.enrollment_status in ('PENDING', 'NOT_ENROLLED'):
            return 'FOLLOW_UP_RECOMMENDED'
        if record.enrollment_status == 'ENROLLED' and record.transfer_status in ('COMPLETED', 'NOT_REQUIRED'):
            return 'CONNECTED'
        return 'PENDING'
    if service_type == 'HEALTHCARE':
        return child.healthcare.continuity_status if child.healthcare else 'PENDING'
    if service_type == 'NUTRITION':
        return child.nutrition.service_status if child.nutrition else 'PENDING'
    if service_type == 'PROTECTION':
        record: ChildProtectionRecord | None = child.protection
        if not record:
            return 'PENDING'
        if record.followup_required or record.protection_status == 'REVIEW_REQUIRED':
            return 'REVIEW_REQUIRED'
        if record.protection_status == 'FOLLOW_UP_RECOMMENDED':
            return 'FOLLOW_UP_RECOMMENDED'
        return 'CONNECTED'
    if service_type == 'WELLBEING':
        return child.wellbeing.support_status if child.wellbeing else 'PENDING'
    record: InclusionRecord | None = child.inclusion
    if not record:
        return 'PENDING'
    if not record.requirement_present:
        return 'CONNECTED'
    return record.support_status


def refresh_child_continuity(
    db: Session,
    child: Child,
    migration: MigrationRecord | None = None,
) -> list[ServiceContinuityRecord]:
    migration = migration or (
        db.query(MigrationRecord)
        .filter(MigrationRecord.family_id == child.family_id)
        .order_by(MigrationRecord.migration_date.desc(), MigrationRecord.created_at.desc())
        .first()
    )
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
        service_status = _service_status(child, service_type)
        action_required = service_status != 'CONNECTED'
        if not record:
            record = ServiceContinuityRecord(
                child_id=child.id,
                migration_id=migration.id if migration else None,
                service_type=service_type,
                status=service_status,
                action_required=action_required,
                assigned_role=SERVICE_ROLES[service_type] if action_required else None,
                due_date=date.today() + timedelta(days=7) if action_required else None,
            )
            db.add(record)
            db.flush()
        else:
            record.status = service_status
            record.action_required = action_required
            record.assigned_role = SERVICE_ROLES[service_type] if action_required else None

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
                        description='Review this service connection with the family and record the outcome.',
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
    migration = (
        db.query(MigrationRecord)
        .filter(MigrationRecord.family_id == child.family_id)
        .order_by(MigrationRecord.migration_date.desc(), MigrationRecord.created_at.desc())
        .first()
    )
    query = db.query(ServiceContinuityRecord).filter(ServiceContinuityRecord.child_id == child.id)
    if migration:
        query = query.filter(ServiceContinuityRecord.migration_id == migration.id)
    else:
        query = query.filter(ServiceContinuityRecord.migration_id.is_(None))
    records = query.order_by(ServiceContinuityRecord.service_type).all()
    if len(records) != 6:
        records = refresh_child_continuity(db, child, migration)
    statuses = {record.status for record in records}
    overall = 'REVIEW_REQUIRED' if 'REVIEW_REQUIRED' in statuses else (
        'FOLLOW_UP_RECOMMENDED'
        if statuses.intersection({'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE'})
        else 'CONNECTED'
    )
    return {
        'child_id': child.id,
        'child_name': f'{child.first_name} {child.last_name}',
        'overall_status': overall,
        'services': records,
        'follow_up_count': sum(record.action_required for record in records),
    }