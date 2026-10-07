from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.continuity_models import Child, Family, FollowUpAction, ServiceContinuityRecord
from app.db.models import User
from app.schemas.continuity import FollowUpCreate, FollowUpOut, FollowUpUpdate
from app.services.continuity_access import ensure_family_access

router = APIRouter(tags=['follow-ups'])
ALLOWED = ('CITIZEN', 'NGO_WORKER', 'ADMIN')


@router.get('/families/{family_id}/followups', response_model=list[FollowUpOut])
def list_followups(
    family_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FollowUpAction]:
    ensure_family_access(db, current_user, family_id, ALLOWED)
    return db.query(FollowUpAction).filter(FollowUpAction.family_id == family_id).order_by(FollowUpAction.due_date).all()


@router.post('/families/{family_id}/followups', response_model=FollowUpOut, status_code=status.HTTP_201_CREATED)
def create_followup(
    family_id: UUID,
    payload: FollowUpCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FollowUpAction:
    ensure_family_access(db, current_user, family_id, ALLOWED)
    if payload.child_id:
        child = db.get(Child, payload.child_id)
        if child is None or child.family_id != family_id:
            raise HTTPException(status_code=404, detail='Child not found in this family.')
    if payload.service_continuity_id:
        continuity = db.get(ServiceContinuityRecord, payload.service_continuity_id)
        if continuity is None or continuity.child.family_id != family_id:
            raise HTTPException(status_code=404, detail='Continuity record not found in this family.')
    followup = FollowUpAction(family_id=family_id, **payload.model_dump())
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@router.put('/followups/{followup_id}', response_model=FollowUpOut)
def update_followup(
    followup_id: UUID,
    payload: FollowUpUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FollowUpAction:
    followup = db.get(FollowUpAction, followup_id)
    if followup is None:
        raise HTTPException(status_code=404, detail='Follow-up item not found.')
    ensure_family_access(db, current_user, followup.family_id, ALLOWED)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(followup, key, value)
    db.commit()
    db.refresh(followup)
    return followup