from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.continuity_models import Child, Family, MigrationRecord
from app.db.models import User
from app.schemas.continuity import MigrationCreate, MigrationOut, MigrationUpdate
from app.services.continuity import refresh_child_continuity
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
    migration = MigrationRecord(family_id=family.id, **payload.model_dump())
    db.add(migration)
    db.flush()
    for child in db.query(Child).filter(Child.family_id == family.id).all():
        refresh_child_continuity(db, child, migration)
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
    return db.query(MigrationRecord).filter(MigrationRecord.family_id == family_id).order_by(MigrationRecord.migration_date.desc()).all()


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
    was_completed = migration.status == 'COMPLETED'
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(migration, key, value)
    if migration.status == 'COMPLETED' and not was_completed:
        family = db.get(Family, migration.family_id)
        if family is not None:
            family.current_district = migration.to_district
            family.current_taluka = migration.to_taluka
            family.current_village_or_city = migration.to_location
    db.commit()
    db.refresh(migration)
    return migration