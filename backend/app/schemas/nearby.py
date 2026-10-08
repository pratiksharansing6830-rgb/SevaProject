import uuid

from pydantic import BaseModel

from app.db.directory_models import OrganizationType, ServiceType


class NearbyServiceResponse(BaseModel):
    """Public service-discovery result. Contains no child, family or user data."""

    organization_id: uuid.UUID
    organization_name: str
    organization_type: OrganizationType
    description: str | None
    address: str | None
    district: str | None
    taluka: str | None
    city_or_village: str | None
    latitude: float | None
    longitude: float | None
    service_id: uuid.UUID
    service_name: str
    service_type: ServiceType
    service_description: str | None
    eligibility: str | None
    contact_information: str | None
    distance_km: float
    is_verified: bool