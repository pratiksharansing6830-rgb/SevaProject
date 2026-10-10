from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.continuity_models import Child, Family, MigrationRecord, ServiceContinuityRecord
from app.db.models import User
from app.schemas.continuity import MigrationCreate, MigrationOut, MigrationUpdate
from app.services.continuity import (
    SERVICE_ROLES,
    _service_reason,
    current_family_migration,
    refresh_child_continuity,
    unresolved_continuity_statuses,
)
from app.services.continuity_access import ensure_family_access

router = APIRouter(tags=['migrations'])


@router.post('/families/{family_id}/migrations', response_model=MigrationOut, status_code=status.HTTP_201_CREATED)
def create_migration(
    family_id: UUID,
    payload: MigrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MigrationRecord:
    family = ensure_family_access(db, current_user, family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    previous_migration = current_family_migration(db, family.id)
    migration = MigrationRecord(family_id=family.id, **payload.model_dump())
    db.add(migration)
    db.flush()
    if payload.status == 'COMPLETED' and current_family_migration(db, family.id).id == migration.id:
        _sync_family_location(family, migration)
    if current_family_migration(db, family.id).id == migration.id:
        for child in db.query(Child).filter(Child.family_id == family.id).all():
            inherited = unresolved_continuity_statuses(db, child, previous_migration)
            refresh_child_continuity(db, child, migration, inherited)
    db.commit()
    db.refresh(migration)
    return migration


@router.get('/families/{family_id}/migrations', response_model=list[MigrationOut])
def list_migrations(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MigrationRecord]:
    ensure_family_access(db, current_user, family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'), allow_grant=False)
    status_order = case(
        (MigrationRecord.status == 'ACTIVE', 0),
        (MigrationRecord.status == 'COMPLETED', 1),
        else_=2,
    )
    return (
        db.query(MigrationRecord)
        .filter(MigrationRecord.family_id == family_id)
        .order_by(status_order, MigrationRecord.migration_date.desc(), MigrationRecord.created_at.desc())
        .all()
    )


@router.get('/migrations/{migration_id}', response_model=MigrationOut)
def get_migration(
    migration_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MigrationRecord:
    migration = db.get(MigrationRecord, migration_id)
    if migration is None:
        raise HTTPException(status_code=404, detail='Migration not found.')
    ensure_family_access(db, current_user, migration.family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'), allow_grant=False)
    return migration


@router.put('/migrations/{migration_id}', response_model=MigrationOut)
def update_migration(
    migration_id: UUID,
    payload: MigrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MigrationRecord:
    migration = db.get(MigrationRecord, migration_id)
    if migration is None:
        raise HTTPException(status_code=404, detail='Migration not found.')
    ensure_family_access(db, current_user, migration.family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'), allow_grant=False)
    previous_status = migration.status
    previous_current = current_family_migration(db, migration.family_id)
    previous_needs = {
        child.id: unresolved_continuity_statuses(db, child, previous_current)
        for child in db.query(Child).filter(Child.family_id == migration.family_id).all()
    }
    updates = payload.model_dump(exclude_unset=True)
    next_status = updates.get('status', migration.status)
    allowed_transitions = {
        'PLANNED': {'PLANNED', 'ACTIVE'},
        'ACTIVE': {'ACTIVE', 'COMPLETED'},
        'COMPLETED': {'COMPLETED'},
    }
    if next_status not in allowed_transitions[migration.status]:
        raise HTTPException(
            status_code=409,
            detail=f"Migration cannot transition from {migration.status} to {next_status}.",
        )
    destination_changed = any(
        updates.get(field, getattr(migration, field)) != getattr(migration, field)
        for field in ('to_district', 'to_taluka', 'to_location')
    )
    for key, value in updates.items():
        setattr(migration, key, value)
    now_current = current_family_migration(db, migration.family_id)
    if (
        now_current is not None
        and now_current.id == migration.id
        and migration.status == 'COMPLETED'
    ):
        family = db.get(Family, migration.family_id)
        if family is not None:
            _sync_family_location(family, migration)

    if destination_changed or migration.status != previous_status:
        _reset_migration_confirmations(db, migration)

    if now_current is not None:
        children = db.query(Child).filter(Child.family_id == migration.family_id).all()
        effective_changed = previous_current is None or previous_current.id != now_current.id
        for child in children:
            inherited = previous_needs.get(child.id, {}) if effective_changed else {}
            refresh_child_continuity(db, child, now_current, inherited)
    db.commit()
    db.refresh(migration)
    return migration


def _sync_family_location(family: Family, migration: MigrationRecord) -> None:
    family.current_district = migration.to_district
    family.current_taluka = migration.to_taluka
    family.current_village_or_city = migration.to_location


def _reset_migration_confirmations(db: Session, migration: MigrationRecord) -> None:
    records = db.query(ServiceContinuityRecord).filter(
        ServiceContinuityRecord.migration_id == migration.id,
        ServiceContinuityRecord.status.in_(('CONNECTED', 'SUPPORT_NOT_REQUIRED')),
    )
    for record in records:
        record.status = 'PENDING'
        record.reason = _service_reason(record.service_type, 'PENDING')
        record.action_required = True
        record.assigned_role = SERVICE_ROLES[record.service_type]
        record.due_date = record.due_date or date.today()
        record.outcome_confirmed_by_user_id = None
        record.outcome_confirmed_at = None
        record.confirmation_method = None
        record.supporting_reference = None