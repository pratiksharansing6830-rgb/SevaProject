import uuid
from enum import Enum

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.continuity_models import TimestampMixin
from app.db.database import Base


class OrganizationType(str, Enum):
    SCHOOL = 'SCHOOL'
    HEALTHCARE = 'HEALTHCARE'
    NGO = 'NGO'
    GOVERNMENT = 'GOVERNMENT'
    NUTRITION_CENTER = 'NUTRITION_CENTER'
    CHILD_SUPPORT = 'CHILD_SUPPORT'
    WELLBEING_SUPPORT = 'WELLBEING_SUPPORT'
    DISABILITY_SUPPORT = 'DISABILITY_SUPPORT'
    COMMUNITY_SERVICE = 'COMMUNITY_SERVICE'
    OTHER = 'OTHER'


class ServiceType(str, Enum):
    EDUCATION = 'EDUCATION'
    HEALTHCARE = 'HEALTHCARE'
    NUTRITION = 'NUTRITION'
    PROTECTION = 'PROTECTION'
    CHILD_SUPPORT = 'CHILD_SUPPORT'
    WELLBEING = 'WELLBEING'
    INCLUSION = 'INCLUSION'
    GOVERNMENT_SCHEME = 'GOVERNMENT_SCHEME'
    SOCIAL_SUPPORT = 'SOCIAL_SUPPORT'
    DOCUMENTATION = 'DOCUMENTATION'
    HOUSING_SUPPORT = 'HOUSING_SUPPORT'
    OTHER = 'OTHER'


def _in_list(enum_cls: type[Enum]) -> str:
    return ', '.join(f"'{item.value}'" for item in enum_cls)


class Organization(TimestampMixin, Base):
    __tablename__ = 'organizations'
    __table_args__ = (
        CheckConstraint(f'organization_type IN ({_in_list(OrganizationType)})', name='ck_organizations_type'),
        CheckConstraint('latitude IS NULL OR (latitude >= -90 AND latitude <= 90)', name='ck_organizations_latitude'),
        CheckConstraint('longitude IS NULL OR (longitude >= -180 AND longitude <= 180)', name='ck_organizations_longitude'),
        Index('ix_organizations_district_taluka', 'district', 'taluka'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    contact_phone: Mapped[str | None] = mapped_column(String(30))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(300))
    address: Mapped[str | None] = mapped_column(String(300))
    district: Mapped[str | None] = mapped_column(String(100))
    taluka: Mapped[str | None] = mapped_column(String(100))
    city_or_village: Mapped[str | None] = mapped_column(String(120))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='false')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')

    services = relationship('Service', back_populates='organization', passive_deletes=True)


class Service(TimestampMixin, Base):
    __tablename__ = 'services'
    __table_args__ = (
        CheckConstraint(f'service_type IN ({_in_list(ServiceType)})', name='ck_services_type'),
        Index('ix_services_org_active', 'organization_id', 'is_active'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('organizations.id', ondelete='RESTRICT'), nullable=False)
    service_name: Mapped[str] = mapped_column(String(160), nullable=False)
    service_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    eligibility: Mapped[str | None] = mapped_column(Text)
    contact_information: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')

    organization = relationship('Organization', back_populates='services')
