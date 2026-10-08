import uuid
from datetime import datetime
from typing import Annotated
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.db.directory_models import OrganizationType, ServiceType

Latitude = Annotated[float, Field(ge=-90, le=90)]
Longitude = Annotated[float, Field(ge=-180, le=180)]


def _check_website(value: str | None) -> str | None:
    if value is None:
        return value
    parsed = urlparse(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError('website must be a valid http or https URL')
    return value


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    organization_name: str = Field(min_length=1, max_length=200)
    organization_type: OrganizationType
    description: str | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    contact_email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=300)
    address: str | None = Field(default=None, max_length=300)
    district: str | None = Field(default=None, max_length=100)
    taluka: str | None = Field(default=None, max_length=100)
    city_or_village: str | None = Field(default=None, max_length=120)
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    is_verified: bool = False
    is_active: bool = True

    _website = field_validator('website')(_check_website)


class OrganizationUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    organization_name: str | None = Field(default=None, min_length=1, max_length=200)
    organization_type: OrganizationType | None = None
    description: str | None = None
    contact_phone: str | None = Field(default=None, max_length=30)
    contact_email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=300)
    address: str | None = Field(default=None, max_length=300)
    district: str | None = Field(default=None, max_length=100)
    taluka: str | None = Field(default=None, max_length=100)
    city_or_village: str | None = Field(default=None, max_length=120)
    latitude: Latitude | None = None
    longitude: Longitude | None = None
    is_verified: bool | None = None
    is_active: bool | None = None

    _website = field_validator('website')(_check_website)

    @model_validator(mode='after')
    def _required_fields_not_null(self):
        for name in ('organization_name', 'organization_type', 'is_verified', 'is_active'):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f'{name} cannot be null')
        return self


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_name: str
    organization_type: OrganizationType
    description: str | None
    contact_phone: str | None
    contact_email: str | None
    website: str | None
    address: str | None
    district: str | None
    taluka: str | None
    city_or_village: str | None
    latitude: float | None
    longitude: float | None
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrganizationSummary(BaseModel):
    """Public provider info embedded in service responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_name: str
    organization_type: OrganizationType
    district: str | None
    taluka: str | None
    city_or_village: str | None
    latitude: float | None
    longitude: float | None
    is_verified: bool


class ServiceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    service_name: str = Field(min_length=1, max_length=160)
    service_type: ServiceType
    description: str | None = None
    eligibility: str | None = None
    contact_information: str | None = Field(default=None, max_length=300)
    is_active: bool = True


class ServiceUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    service_name: str | None = Field(default=None, min_length=1, max_length=160)
    service_type: ServiceType | None = None
    description: str | None = None
    eligibility: str | None = None
    contact_information: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None

    @model_validator(mode='after')
    def _required_fields_not_null(self):
        for name in ('service_name', 'service_type', 'is_active'):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f'{name} cannot be null')
        return self


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    service_name: str
    service_type: ServiceType
    description: str | None
    eligibility: str | None
    contact_information: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    organization: OrganizationSummary | None = None