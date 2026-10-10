from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

EnrollmentStatus = Literal['ENROLLED', 'PENDING', 'NOT_ENROLLED', 'UNKNOWN']
TransferStatus = Literal['COMPLETED', 'PENDING', 'NOT_STARTED', 'NOT_REQUIRED']
ServiceStatus = Literal['CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE']
ProtectionStatus = Literal['NO_ACTION_RECORDED', 'FOLLOW_UP_RECOMMENDED', 'SUPPORT_CONNECTED', 'REVIEW_REQUIRED']
ContinuityStatus = Literal['CONNECTED', 'PENDING', 'FOLLOW_UP_REQUIRED', 'SUPPORT_NOT_REQUIRED', 'REVIEW_REQUIRED']
ConfirmationMethod = Literal['FAMILY_REPORT', 'SERVICE_PROVIDER', 'DOCUMENT_REVIEW', 'IN_PERSON', 'OTHER']
ServiceType = Literal['EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION']


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class FamilyCreate(BaseModel):
    family_name: str = Field(min_length=2, max_length=120)
    contact_mobile: str = Field(min_length=8, max_length=30)
    current_district: str = Field(min_length=1, max_length=100)
    current_taluka: str = Field(min_length=1, max_length=100)
    current_village_or_city: str = Field(min_length=1, max_length=120)
    current_address: str | None = Field(default=None, max_length=300)
    preferred_language: str = Field(default='English', min_length=2, max_length=30)


class FamilyUpdate(BaseModel):
    family_name: str | None = Field(default=None, min_length=2, max_length=120)
    contact_mobile: str | None = Field(default=None, min_length=8, max_length=30)
    current_district: str | None = Field(default=None, min_length=1, max_length=100)
    current_taluka: str | None = Field(default=None, min_length=1, max_length=100)
    current_village_or_city: str | None = Field(default=None, min_length=1, max_length=120)
    current_address: str | None = Field(default=None, max_length=300)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=30)


class FamilyOut(ORMModel):
    id: UUID
    family_reference_id: str
    primary_guardian_user_id: UUID
    family_name: str
    contact_mobile: str
    current_district: str
    current_taluka: str
    current_village_or_city: str
    current_address: str | None
    preferred_language: str
    created_at: datetime
    updated_at: datetime


class FamilyAccessCreate(BaseModel):
    user_id: UUID


class ChildCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    date_of_birth: date
    gender: Literal['FEMALE', 'MALE', 'NON_BINARY', 'UNDISCLOSED'] = 'UNDISCLOSED'
    education_status: EnrollmentStatus = 'UNKNOWN'
    current_class: str | None = Field(default=None, max_length=30)
    preferred_language: str = Field(default='English', min_length=2, max_length=30)
    disability_or_inclusion_requirement: str | None = Field(default=None, max_length=500)


class ChildUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=80)
    last_name: str | None = Field(default=None, min_length=1, max_length=80)
    date_of_birth: date | None = None
    gender: Literal['FEMALE', 'MALE', 'NON_BINARY', 'UNDISCLOSED'] | None = None
    education_status: EnrollmentStatus | None = None
    current_class: str | None = Field(default=None, max_length=30)
    preferred_language: str | None = Field(default=None, min_length=2, max_length=30)
    disability_or_inclusion_requirement: str | None = Field(default=None, max_length=500)


class ChildOut(ORMModel):
    id: UUID
    family_id: UUID
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    education_status: str
    current_class: str | None
    preferred_language: str
    disability_or_inclusion_requirement: str | None
    created_at: datetime
    updated_at: datetime


class MigrationCreate(BaseModel):
    from_district: str = Field(min_length=1, max_length=100)
    from_taluka: str = Field(min_length=1, max_length=100)
    from_location: str = Field(min_length=1, max_length=120)
    to_district: str = Field(min_length=1, max_length=100)
    to_taluka: str = Field(min_length=1, max_length=100)
    to_location: str = Field(min_length=1, max_length=120)
    migration_date: date
    migration_reason: str | None = Field(default=None, max_length=300)
    status: Literal['PLANNED', 'ACTIVE'] = 'ACTIVE'


class MigrationUpdate(BaseModel):
    from_district: str | None = Field(default=None, min_length=1, max_length=100)
    from_taluka: str | None = Field(default=None, min_length=1, max_length=100)
    from_location: str | None = Field(default=None, min_length=1, max_length=120)
    to_district: str | None = Field(default=None, min_length=1, max_length=100)
    to_taluka: str | None = Field(default=None, min_length=1, max_length=100)
    to_location: str | None = Field(default=None, min_length=1, max_length=120)
    migration_date: date | None = None
    migration_reason: str | None = Field(default=None, max_length=300)
    status: Literal['PLANNED', 'ACTIVE', 'COMPLETED'] | None = None


class MigrationOut(ORMModel):
    id: UUID
    family_id: UUID
    from_district: str
    from_taluka: str
    from_location: str
    to_district: str
    to_taluka: str
    to_location: str
    migration_date: date
    migration_reason: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class EducationCreate(BaseModel):
    previous_school_name: str | None = Field(default=None, max_length=160)
    previous_school_location: str | None = Field(default=None, max_length=160)
    current_school_name: str | None = Field(default=None, max_length=160)
    current_school_location: str | None = Field(default=None, max_length=160)
    current_class: str | None = Field(default=None, max_length=30)
    enrollment_status: EnrollmentStatus = 'UNKNOWN'
    transfer_status: TransferStatus = 'NOT_STARTED'
    last_attendance_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class EducationUpdate(EducationCreate):
    pass


class EducationOut(ORMModel):
    id: UUID
    child_id: UUID
    previous_school_name: str | None
    previous_school_location: str | None
    current_school_name: str | None
    current_school_location: str | None
    current_class: str | None
    enrollment_status: str
    transfer_status: str
    last_attendance_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class HealthcareCreate(BaseModel):
    healthcare_provider_name: str | None = Field(default=None, max_length=160)
    healthcare_location: str | None = Field(default=None, max_length=160)
    continuity_status: ServiceStatus = 'PENDING'
    last_followup_date: date | None = None
    next_followup_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class HealthcareUpdate(HealthcareCreate):
    pass


class HealthcareOut(ORMModel):
    id: UUID
    child_id: UUID
    healthcare_provider_name: str | None
    healthcare_location: str | None
    continuity_status: str
    last_followup_date: date | None
    next_followup_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class NutritionCreate(BaseModel):
    nutrition_service_name: str | None = Field(default=None, max_length=160)
    nutrition_service_location: str | None = Field(default=None, max_length=160)
    service_status: ServiceStatus = 'PENDING'
    last_service_date: date | None = None
    next_service_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class NutritionUpdate(NutritionCreate):
    pass


class NutritionOut(ORMModel):
    id: UUID
    child_id: UUID
    nutrition_service_name: str | None
    nutrition_service_location: str | None
    service_status: str
    last_service_date: date | None
    next_service_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class WellbeingCreate(BaseModel):
    support_status: ServiceStatus = 'PENDING'
    support_provider: str | None = Field(default=None, max_length=160)
    last_followup_date: date | None = None
    next_followup_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class WellbeingUpdate(WellbeingCreate):
    pass


class WellbeingOut(ORMModel):
    id: UUID
    child_id: UUID
    support_status: str
    support_provider: str | None
    last_followup_date: date | None
    next_followup_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ProtectionCreate(BaseModel):
    protection_status: ProtectionStatus = 'NO_ACTION_RECORDED'
    support_contact_available: bool = False
    last_review_date: date | None = None
    followup_required: bool = False
    notes: str | None = Field(default=None, max_length=2000)


class ProtectionUpdate(ProtectionCreate):
    pass


class ProtectionOut(ORMModel):
    id: UUID
    child_id: UUID
    protection_status: str
    support_contact_available: bool
    last_review_date: date | None
    followup_required: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime


class InclusionCreate(BaseModel):
    requirement_present: bool | None = None
    support_type: Literal['ACCESSIBILITY', 'LEARNING_SUPPORT', 'MOBILITY_SUPPORT', 'COMMUNICATION_SUPPORT', 'OTHER'] = 'OTHER'
    support_status: ServiceStatus = 'PENDING'
    notes: str | None = Field(default=None, max_length=2000)


class InclusionUpdate(InclusionCreate):
    pass


class InclusionOut(ORMModel):
    id: UUID
    child_id: UUID
    requirement_present: bool | None
    support_type: str
    support_status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ContinuityUpdate(BaseModel):
    status: ContinuityStatus
    confirmation_method: ConfirmationMethod | None = None
    supporting_reference: str | None = Field(
        default=None,
        max_length=200,
        description='Short, non-sensitive reference identifier only; do not include personal or case details.',
    )
    due_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode='after')
    def validate_outcome_confirmation(self):
        terminal_status = self.status in ('CONNECTED', 'SUPPORT_NOT_REQUIRED')
        if terminal_status and self.confirmation_method is None:
            raise ValueError('A confirmation method is required for a confirmed outcome.')
        if not terminal_status and (self.confirmation_method is not None or self.supporting_reference is not None):
            raise ValueError('Confirmation details are only accepted for a confirmed outcome.')
        return self


class ServiceContinuityOut(ORMModel):
    id: UUID
    child_id: UUID
    migration_id: UUID | None
    service_type: ServiceType
    status: ContinuityStatus
    reason: str | None
    action_required: bool
    assigned_role: str | None
    due_date: date | None
    notes: str | None
    outcome_confirmed_by_user_id: UUID | None
    outcome_confirmed_at: datetime | None
    confirmation_method: ConfirmationMethod | None
    supporting_reference: str | None


class ContinuitySummary(BaseModel):
    child_id: UUID
    child_name: str
    overall_status: Literal['CONNECTED', 'SUPPORT_NOT_REQUIRED', 'FOLLOW_UP_REQUIRED', 'REVIEW_REQUIRED']
    services: list[ServiceContinuityOut]
    follow_up_count: int


class FollowUpCreate(BaseModel):
    child_id: UUID | None = None
    service_continuity_id: UUID | None = None
    title: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    status: Literal['OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'] = 'OPEN'
    priority: Literal['LOW', 'MEDIUM', 'HIGH'] = 'MEDIUM'
    due_date: date | None = None
    assigned_role: Literal['CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN'] | None = None


class FollowUpUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    status: Literal['OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'] | None = None
    priority: Literal['LOW', 'MEDIUM', 'HIGH'] | None = None
    due_date: date | None = None
    assigned_role: Literal['CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN'] | None = None


class FollowUpOut(ORMModel):
    id: UUID
    family_id: UUID
    child_id: UUID | None
    service_continuity_id: UUID | None
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date | None
    assigned_role: str | None
    created_at: datetime
    updated_at: datetime