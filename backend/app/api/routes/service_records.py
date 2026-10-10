from typing import TypeVar
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.continuity_models import (
    Child,
    ChildProtectionRecord,
    EducationRecord,
    HealthcareContinuity,
    InclusionRecord,
    NutritionRecord,
    ServiceContinuityRecord,
    WellBeingRecord,
)
from app.db.models import User
from app.schemas.continuity import (
    EducationCreate,
    EducationOut,
    EducationUpdate,
    HealthcareCreate,
    HealthcareOut,
    HealthcareUpdate,
    InclusionCreate,
    InclusionOut,
    InclusionUpdate,
    NutritionCreate,
    NutritionOut,
    NutritionUpdate,
    ProtectionCreate,
    ProtectionOut,
    ProtectionUpdate,
    WellbeingCreate,
    WellbeingOut,
    WellbeingUpdate,
)
from app.services.continuity_access import ensure_child_access
from app.services.continuity import _service_status, refresh_child_continuity

router = APIRouter(tags=['service continuity'])
ModelT = TypeVar('ModelT')
SERVICE_TYPES = {
    EducationRecord: 'EDUCATION',
    HealthcareContinuity: 'HEALTHCARE',
    NutritionRecord: 'NUTRITION',
    ChildProtectionRecord: 'PROTECTION',
    WellBeingRecord: 'WELLBEING',
    InclusionRecord: 'INCLUSION',
}


def _create_record(db: Session, child: Child, model: type[ModelT], payload: BaseModel) -> ModelT:
    existing = db.query(model).filter_by(child_id=child.id).first()
    if existing:
        raise HTTPException(status_code=409, detail='A service record already exists. Update the existing record instead.')
    record = model(child_id=child.id, **payload.model_dump())
    record.updated_at = datetime.now(timezone.utc)
    db.add(record)
    db.flush()
    refresh_child_continuity(db, child)
    db.commit()
    db.refresh(record)
    return record


def _get_record(db: Session, record_id: UUID, model: type[ModelT]) -> ModelT:
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail='Service record not found.')
    return record


def _update_record(db: Session, child: Child, record: ModelT, payload: BaseModel) -> ModelT:
    service_type = SERVICE_TYPES[type(record)]
    previous_status = _service_status(child, service_type)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.flush()
    if previous_status != _service_status(child, service_type):
        record.updated_at = datetime.now(timezone.utc)
        db.flush()
    refresh_child_continuity(db, child)
    db.commit()
    db.refresh(record)
    return record


@router.post('/children/{child_id}/education', response_model=EducationOut, status_code=status.HTTP_201_CREATED)
def create_education(child_id: UUID, payload: EducationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'SCHOOL', 'NGO_WORKER', 'ADMIN'))
    return _create_record(db, child, EducationRecord, payload)


@router.get('/children/{child_id}/education', response_model=EducationOut | None)
def get_education(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'SCHOOL', 'NGO_WORKER', 'ADMIN'))
    return child.education


@router.put('/education/{record_id}', response_model=EducationOut)
def update_education(record_id: UUID, payload: EducationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = _get_record(db, record_id, EducationRecord)
    ensure_child_access(db, current_user, record.child_id, ('CITIZEN', 'SCHOOL', 'NGO_WORKER', 'ADMIN'))
    return _update_record(db, record.child, record, payload)


@router.post('/children/{child_id}/healthcare', response_model=HealthcareOut, status_code=status.HTTP_201_CREATED)
def create_healthcare(child_id: UUID, payload: HealthcareCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'HEALTHCARE', 'NGO_WORKER', 'ADMIN'))
    return _create_record(db, child, HealthcareContinuity, payload)


@router.get('/children/{child_id}/healthcare', response_model=HealthcareOut | None)
def get_healthcare(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'HEALTHCARE', 'NGO_WORKER', 'ADMIN'))
    return child.healthcare


@router.put('/healthcare/{record_id}', response_model=HealthcareOut)
def update_healthcare(record_id: UUID, payload: HealthcareUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = _get_record(db, record_id, HealthcareContinuity)
    ensure_child_access(db, current_user, record.child_id, ('CITIZEN', 'HEALTHCARE', 'NGO_WORKER', 'ADMIN'))
    return _update_record(db, record.child, record, payload)


@router.post('/children/{child_id}/nutrition', response_model=NutritionOut, status_code=status.HTTP_201_CREATED)
def create_nutrition(child_id: UUID, payload: NutritionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _create_record(db, child, NutritionRecord, payload)


@router.get('/children/{child_id}/nutrition', response_model=NutritionOut | None)
def get_nutrition(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return child.nutrition


@router.put('/nutrition/{record_id}', response_model=NutritionOut)
def update_nutrition(record_id: UUID, payload: NutritionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = _get_record(db, record_id, NutritionRecord)
    ensure_child_access(db, current_user, record.child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _update_record(db, record.child, record, payload)


@router.post('/children/{child_id}/wellbeing', response_model=WellbeingOut, status_code=status.HTTP_201_CREATED)
def create_wellbeing(child_id: UUID, payload: WellbeingCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _create_record(db, child, WellBeingRecord, payload)


@router.get('/children/{child_id}/wellbeing', response_model=WellbeingOut | None)
def get_wellbeing(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return child.wellbeing


@router.put('/wellbeing/{record_id}', response_model=WellbeingOut)
def update_wellbeing(record_id: UUID, payload: WellbeingUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = _get_record(db, record_id, WellBeingRecord)
    ensure_child_access(db, current_user, record.child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _update_record(db, record.child, record, payload)


@router.post('/children/{child_id}/protection', response_model=ProtectionOut, status_code=status.HTTP_201_CREATED)
def create_protection(child_id: UUID, payload: ProtectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _create_record(db, child, ChildProtectionRecord, payload)


@router.get('/children/{child_id}/protection', response_model=ProtectionOut | None)
def get_protection(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return child.protection


@router.put('/protection/{record_id}', response_model=ProtectionOut)
def update_protection(record_id: UUID, payload: ProtectionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = _get_record(db, record_id, ChildProtectionRecord)
    ensure_child_access(db, current_user, record.child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _update_record(db, record.child, record, payload)


@router.post('/children/{child_id}/inclusion', response_model=InclusionOut, status_code=status.HTTP_201_CREATED)
def create_inclusion(child_id: UUID, payload: InclusionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _create_record(db, child, InclusionRecord, payload)


@router.get('/children/{child_id}/inclusion', response_model=InclusionOut | None)
def get_inclusion(child_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    child = ensure_child_access(db, current_user, child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return child.inclusion


@router.put('/inclusion/{record_id}', response_model=InclusionOut)
def update_inclusion(record_id: UUID, payload: InclusionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = _get_record(db, record_id, InclusionRecord)
    ensure_child_access(db, current_user, record.child_id, ('CITIZEN', 'NGO_WORKER', 'ADMIN'))
    return _update_record(db, record.child, record, payload)