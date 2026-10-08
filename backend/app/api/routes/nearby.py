from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, contains_eager

from app.api.deps import get_current_user, get_db
from app.db.directory_models import Organization, Service, ServiceType
from app.db.models import User
from app.schemas.nearby import NearbyServiceResponse
from app.services.geo import distances_km, latitude_window

router = APIRouter(tags=['nearby'])

DEFAULT_RADIUS_KM = 10.0
MAX_RADIUS_KM = 500.0


@router.get('/services/nearby', response_model=list[NearbyServiceResponse])
def nearby_services(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius: float = Query(DEFAULT_RADIUS_KM, gt=0, le=MAX_RADIUS_KM, description='Search radius in kilometres'),
    service_type: ServiceType | None = None,
    district: str | None = None,
    taluka: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NearbyServiceResponse]:
    # The search coordinates are used only for this calculation. They are never stored or logged.
    min_lat, max_lat = latitude_window(latitude, radius)
    query = (
        db.query(Service)
        .join(Organization, Service.organization_id == Organization.id)
        .options(contains_eager(Service.organization))
        .filter(
            Service.is_active.is_(True),
            Organization.is_active.is_(True),
            Organization.latitude.isnot(None),
            Organization.longitude.isnot(None),
            Organization.latitude.between(min_lat, max_lat),
        )
    )
    if service_type is not None:
        query = query.filter(Service.service_type == service_type.value)
    if district:
        query = query.filter(func.lower(Organization.district) == district.strip().lower())
    if taluka:
        query = query.filter(func.lower(Organization.taluka) == taluka.strip().lower())
    services = query.all()

    organizations = {service.organization.id: service.organization for service in services}
    distances = distances_km(db, latitude, longitude, organizations.values())

    results: list[NearbyServiceResponse] = []
    for service in services:
        org = service.organization
        distance = distances[org.id]
        if distance > radius:
            continue
        results.append(
            NearbyServiceResponse(
                organization_id=org.id,
                organization_name=org.organization_name,
                organization_type=org.organization_type,
                description=org.description,
                address=org.address,
                district=org.district,
                taluka=org.taluka,
                city_or_village=org.city_or_village,
                latitude=org.latitude,
                longitude=org.longitude,
                service_id=service.id,
                service_name=service.service_name,
                service_type=service.service_type,
                service_description=service.description,
                eligibility=service.eligibility,
                contact_information=service.contact_information,
                distance_km=round(distance, 2),
                is_verified=org.is_verified,
            )
        )
    results.sort(key=lambda item: (item.distance_km, item.service_name))
    return results