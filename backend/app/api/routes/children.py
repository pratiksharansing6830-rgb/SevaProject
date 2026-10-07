from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.continuity_models import Child, Family, FamilyMember
from app.db.models import User
from app.schemas.continuity import ChildCreate, ChildOut, ChildUpdate
from app.services.continuity_access import ensure_child_access, ensure_family_access

router = APIRouter(tags=['children'])


@router.post('/families/{family_id}/children', response_model=ChildOut, status_code=status.HTTP_201_CREATED)
def create_child(
    family_id: UUID,
    payload: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Child:
    family = ensure_family_access(db, current_user, family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    child = Child(family_id=family.id, **payload.model_dump())
    db.add(child)
    db.flush()
    db.add(FamilyMember(family_id=family.id, child_id=child.id, relationship_type='CHILD'))
    db.commit()
    db.refresh(child)
    return child


@router.get('/families/{family_id}/children', response_model=list[ChildOut])
def list_children(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Child]:
    ensure_family_access(db, current_user, family_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'), allow_grant=False)
    return db.query(Child).filter(Child.family_id == family_id).order_by(Child.created_at).all()


@router.get('/children/{child_id}', response_model=ChildOut)
def get_child(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Child:
    return ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))


@router.put('/children/{child_id}', response_model=ChildOut)
def update_child(
    child_id: UUID,
    payload: ChildUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Child:
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(child, key, value)
    db.commit()
    db.refresh(child)
    return child