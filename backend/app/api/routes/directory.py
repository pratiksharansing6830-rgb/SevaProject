from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, contains_eager

from app.api.deps import get_current_user, get_db, require_role
from app.db.directory_models import Organization, OrganizationType, Service, ServiceType
from app.db.models import User
from app.schemas.directory import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    ServiceCreate,
    ServiceResponse,
    ServiceUpdate,
)

router = APIRouter(tags=['directory'])


def _ci_equals(column, value: str):
    return func.lower(column) == value.strip().lower()


def _get_organization(db: Session, organization_id: UUID, *, active_only: bool) -> Organization:
    organization = db.get(Organization, organization_id)
    if organization is None or (active_only and not organization.is_active):
        raise HTTPException(status_code=404, detail='Organization not found.')
    return organization


# ---------------------------------------------------------------- organizations

@router.post('/organizations', response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(require_role('ADMIN')),
    db: Session = Depends(get_db),
) -> Organization:
    organization = Organization(**payload.model_dump(mode='json'))
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


@router.get('/organizations', response_model=list[OrganizationResponse])
def list_organizations(
    organization_type: OrganizationType | None = None,
    district: str | None = None,
    taluka: str | None = None,
    city_or_village: str | None = None,
    is_verified: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Organization]:
    query = db.query(Organization).filter(Organization.is_active.is_(True))
    if organization_type is not None:
        query = query.filter(Organization.organization_type == organization_type.value)
    if district:
        query = query.filter(_ci_equals(Organization.district, district))
    if taluka:
        query = query.filter(_ci_equals(Organization.taluka, taluka))
    if city_or_village:
        query = query.filter(_ci_equals(Organization.city_or_village, city_or_village))
    if is_verified is not None:
        query = query.filter(Organization.is_verified.is_(is_verified))
    return query.order_by(Organization.organization_name).all()


@router.put('/organizations/{organization_id}', response_model=OrganizationResponse)
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    current_user: User = Depends(require_role('ADMIN')),
    db: Session = Depends(get_db),
) -> Organization:
    organization = _get_organization(db, organization_id, active_only=False)
    for key, value in payload.model_dump(exclude_unset=True, mode='json').items():
        setattr(organization, key, value)
    db.commit()
    db.refresh(organization)
    return organization


# --------------------------------------------------------------------- services

@router.get('/services', response_model=list[ServiceResponse])
def list_services(
    service_type: ServiceType | None = None,
    district: str | None = None,
    taluka: str | None = None,
    organization_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Service]:
    # Services of inactive organizations are never exposed.
    query = (
        db.query(Service)
        .join(Organization, Service.organization_id == Organization.id)
        .options(contains_eager(Service.organization))
        .filter(Service.is_active.is_(True), Organization.is_active.is_(True))
    )
    if service_type is not None:
        query = query.filter(Service.service_type == service_type.value)
    if district:
        query = query.filter(_ci_equals(Organization.district, district))
    if taluka:
        query = query.filter(_ci_equals(Organization.taluka, taluka))
    if organization_id is not None:
        query = query.filter(Service.organization_id == organization_id)
    return query.order_by(Service.service_name).all()


@router.post(
    '/organizations/{organization_id}/services',
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    organization_id: UUID,
    payload: ServiceCreate,
    current_user: User = Depends(require_role('ADMIN')),
    db: Session = Depends(get_db),
) -> Service:
    organization = _get_organization(db, organization_id, active_only=False)
    service = Service(organization_id=organization.id, **payload.model_dump(mode='json'))
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get('/organizations/{organization_id}/services', response_model=list[ServiceResponse])
def list_organization_services(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Service]:
    organization = _get_organization(db, organization_id, active_only=True)
    return (
        db.query(Service)
        .filter(Service.organization_id == organization.id, Service.is_active.is_(True))
        .order_by(Service.service_name)
        .all()
    )


@router.put('/organizations/{organization_id}/services/{service_id}', response_model=ServiceResponse)
def update_service(
    organization_id: UUID,
    service_id: UUID,
    payload: ServiceUpdate,
    current_user: User = Depends(require_role('ADMIN')),
    db: Session = Depends(get_db),
) -> Service:
    _get_organization(db, organization_id, active_only=False)
    service = (
        db.query(Service)
        .filter(Service.id == service_id, Service.organization_id == organization_id)
        .first()
    )
    if service is None:
        raise HTTPException(status_code=404, detail='Service not found for this organization.')
    for key, value in payload.model_dump(exclude_unset=True, mode='json').items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service