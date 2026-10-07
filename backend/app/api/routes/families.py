import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.db.continuity_models import Family, FamilyAccess, FamilyMember
from app.db.models import User
from app.schemas.continuity import FamilyAccessCreate, FamilyCreate, FamilyOut, FamilyUpdate
from app.services.continuity_access import ensure_family_access

router = APIRouter(tags=['families'])


@router.post('/families', response_model=FamilyOut, status_code=status.HTTP_201_CREATED)
def create_family(
    payload: FamilyCreate,
    current_user: User = Depends(require_role('CITIZEN', 'ADMIN')),
    db: Session = Depends(get_db),
) -> Family:
    family = Family(
        **payload.model_dump(),
        primary_guardian_user_id=current_user.id,
        family_reference_id=f'SAH-{uuid.uuid4().hex[:10].upper()}',
    )
    db.add(family)
    db.flush()
    db.add(FamilyMember(family_id=family.id, user_id=current_user.id, relationship_type='GUARDIAN'))
    db.commit()
    db.refresh(family)
    return family


@router.get('/families', response_model=list[FamilyOut])
def list_families(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Family]:
    if current_user.role.value == 'ADMIN':
        return db.query(Family).order_by(Family.created_at.desc()).all()
    if current_user.role.value == 'CITIZEN':
        return db.query(Family).filter(Family.primary_guardian_user_id == current_user.id).order_by(Family.created_at.desc()).all()
    if current_user.role.value == 'NGO_WORKER':
        return (
            db.query(Family)
            .join(FamilyAccess, FamilyAccess.family_id == Family.id)
            .filter(FamilyAccess.user_id == current_user.id, FamilyAccess.access_role == 'NGO_WORKER')
            .order_by(Family.created_at.desc())
            .all()
        )
    raise HTTPException(status_code=403, detail='Your role cannot list family records.')


@router.get('/families/{family_id}', response_model=FamilyOut)
def get_family(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Family:
    return ensure_family_access(db, current_user, family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'), allow_grant=False)


@router.put('/families/{family_id}', response_model=FamilyOut)
def update_family(
    family_id: UUID,
    payload: FamilyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Family:
    family = ensure_family_access(db, current_user, family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'), allow_grant=False)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(family, key, value)
    db.commit()
    db.refresh(family)
    return family


@router.post('/families/{family_id}/access/{user_id}', status_code=status.HTTP_201_CREATED)
def grant_family_access(
    family_id: UUID,
    user_id: UUID,
    payload: FamilyAccessCreate,
    current_user: User = Depends(require_role('ADMIN')),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if user_id != payload.user_id:
        raise HTTPException(status_code=400, detail='The path and body user IDs must match.')
    family = db.get(Family, family_id)
    staff_user = db.get(User, user_id)
    if family is None or staff_user is None:
        raise HTTPException(status_code=404, detail='Family or user not found.')
    if staff_user.role.value not in ('SCHOOL', 'HEALTHCARE', 'NGO_WORKER'):
        raise HTTPException(status_code=400, detail='Only service staff can be assigned to a family.')
    existing = db.query(FamilyAccess).filter_by(family_id=family_id, user_id=user_id).first()
    if existing:
        existing.access_role = staff_user.role.value
    else:
        db.add(FamilyAccess(
            family_id=family_id,
            user_id=user_id,
            access_role=staff_user.role.value,
            granted_by_user_id=current_user.id,
        ))
    db.commit()
    return {'status': 'assigned', 'access_role': staff_user.role.value}