import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.db.models import User


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Family(TimestampMixin, Base):
    __tablename__ = 'families'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_reference_id: Mapped[str] = mapped_column(String(24), unique=True, nullable=False, index=True)
    primary_guardian_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    family_name: Mapped[str] = mapped_column(String(120), nullable=False)
    contact_mobile: Mapped[str] = mapped_column(String(30), nullable=False)
    current_district: Mapped[str] = mapped_column(String(100), nullable=False)
    current_taluka: Mapped[str] = mapped_column(String(100), nullable=False)
    current_village_or_city: Mapped[str] = mapped_column(String(120), nullable=False)
    current_address: Mapped[str | None] = mapped_column(String(300))
    preferred_language: Mapped[str] = mapped_column(String(30), nullable=False, default='English')

    guardian = relationship('User', foreign_keys=[primary_guardian_user_id])
    children = relationship('Child', back_populates='family', passive_deletes=True)
    migrations = relationship('MigrationRecord', back_populates='family', passive_deletes=True)
    members = relationship('FamilyMember', back_populates='family', passive_deletes=True)


class FamilyMember(TimestampMixin, Base):
    __tablename__ = 'family_members'
    __table_args__ = (
        CheckConstraint("relationship_type IN ('GUARDIAN', 'PARENT', 'CHILD')", name='ck_family_members_relationship'),
        CheckConstraint(
            '(user_id IS NOT NULL AND child_id IS NULL) OR (user_id IS NULL AND child_id IS NOT NULL)',
            name='ck_family_members_subject',
        ),
        UniqueConstraint('family_id', 'user_id', name='uq_family_member_user'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('families.id', ondelete='RESTRICT'), nullable=False, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'))
    child_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'))
    relationship_type: Mapped[str] = mapped_column(String(20), nullable=False)

    family = relationship('Family', back_populates='members')
    user = relationship('User')
    child = relationship('Child', foreign_keys=[child_id])


class FamilyAccess(TimestampMixin, Base):
    __tablename__ = 'family_access'
    __table_args__ = (
        CheckConstraint("access_role IN ('SCHOOL', 'HEALTHCARE', 'NGO_WORKER')", name='ck_family_access_role'),
        UniqueConstraint('family_id', 'user_id', name='uq_family_access_user'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('families.id', ondelete='RESTRICT'), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    access_role: Mapped[str] = mapped_column(String(20), nullable=False)
    granted_by_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)

    family = relationship('Family')
    user = relationship('User', foreign_keys=[user_id])


class Child(TimestampMixin, Base):
    __tablename__ = 'children'
    __table_args__ = (
        CheckConstraint("gender IN ('FEMALE', 'MALE', 'NON_BINARY', 'UNDISCLOSED')", name='ck_children_gender'),
        CheckConstraint("education_status IN ('ENROLLED', 'PENDING', 'NOT_ENROLLED', 'UNKNOWN')", name='ck_children_education_status'),
        Index('ix_children_family_id', 'family_id'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('families.id', ondelete='RESTRICT'), nullable=False)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False, default='UNDISCLOSED')
    education_status: Mapped[str] = mapped_column(String(20), nullable=False, default='UNKNOWN')
    current_class: Mapped[str | None] = mapped_column(String(30))
    preferred_language: Mapped[str] = mapped_column(String(30), nullable=False, default='English')
    disability_or_inclusion_requirement: Mapped[str | None] = mapped_column(String(500))

    family = relationship('Family', back_populates='children')
    education = relationship('EducationRecord', back_populates='child', uselist=False, passive_deletes=True)
    healthcare = relationship('HealthcareContinuity', back_populates='child', uselist=False, passive_deletes=True)
    nutrition = relationship('NutritionRecord', back_populates='child', uselist=False, passive_deletes=True)
    wellbeing = relationship('WellBeingRecord', back_populates='child', uselist=False, passive_deletes=True)
    protection = relationship('ChildProtectionRecord', back_populates='child', uselist=False, passive_deletes=True)
    inclusion = relationship('InclusionRecord', back_populates='child', uselist=False, passive_deletes=True)
    continuity_records = relationship('ServiceContinuityRecord', back_populates='child', passive_deletes=True)


class MigrationRecord(TimestampMixin, Base):
    __tablename__ = 'migration_records'
    __table_args__ = (
        CheckConstraint("status IN ('PLANNED', 'ACTIVE', 'COMPLETED')", name='ck_migrations_status'),
        Index('ix_migrations_family_id', 'family_id'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('families.id', ondelete='RESTRICT'), nullable=False)
    from_district: Mapped[str] = mapped_column(String(100), nullable=False)
    from_taluka: Mapped[str] = mapped_column(String(100), nullable=False)
    from_location: Mapped[str] = mapped_column(String(120), nullable=False)
    to_district: Mapped[str] = mapped_column(String(100), nullable=False)
    to_taluka: Mapped[str] = mapped_column(String(100), nullable=False)
    to_location: Mapped[str] = mapped_column(String(120), nullable=False)
    migration_date: Mapped[date] = mapped_column(Date, nullable=False)
    migration_reason: Mapped[str | None] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='ACTIVE')

    family = relationship('Family', back_populates='migrations')
    continuity_records = relationship('ServiceContinuityRecord', back_populates='migration', passive_deletes=True)


class EducationRecord(TimestampMixin, Base):
    __tablename__ = 'education_records'
    __table_args__ = (
        CheckConstraint("enrollment_status IN ('ENROLLED', 'PENDING', 'NOT_ENROLLED', 'UNKNOWN')", name='ck_education_enrollment'),
        CheckConstraint("transfer_status IN ('COMPLETED', 'PENDING', 'NOT_STARTED', 'NOT_REQUIRED')", name='ck_education_transfer'),
        UniqueConstraint('child_id', name='uq_education_child'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    previous_school_name: Mapped[str | None] = mapped_column(String(160))
    previous_school_location: Mapped[str | None] = mapped_column(String(160))
    current_school_name: Mapped[str | None] = mapped_column(String(160))
    current_school_location: Mapped[str | None] = mapped_column(String(160))
    current_class: Mapped[str | None] = mapped_column(String(30))
    enrollment_status: Mapped[str] = mapped_column(String(20), nullable=False, default='UNKNOWN')
    transfer_status: Mapped[str] = mapped_column(String(20), nullable=False, default='NOT_STARTED')
    last_attendance_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    child = relationship('Child', back_populates='education')


class HealthcareContinuity(TimestampMixin, Base):
    __tablename__ = 'healthcare_continuity'
    __table_args__ = (
        CheckConstraint("continuity_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_healthcare_status'),
        UniqueConstraint('child_id', name='uq_healthcare_child'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    healthcare_provider_name: Mapped[str | None] = mapped_column(String(160))
    healthcare_location: Mapped[str | None] = mapped_column(String(160))
    continuity_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
    last_followup_date: Mapped[date | None] = mapped_column(Date)
    next_followup_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    child = relationship('Child', back_populates='healthcare')


class NutritionRecord(TimestampMixin, Base):
    __tablename__ = 'nutrition_records'
    __table_args__ = (
        CheckConstraint("service_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_nutrition_status'),
        UniqueConstraint('child_id', name='uq_nutrition_child'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    nutrition_service_name: Mapped[str | None] = mapped_column(String(160))
    nutrition_service_location: Mapped[str | None] = mapped_column(String(160))
    service_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
    last_service_date: Mapped[date | None] = mapped_column(Date)
    next_service_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    child = relationship('Child', back_populates='nutrition')


class WellBeingRecord(TimestampMixin, Base):
    __tablename__ = 'wellbeing_records'
    __table_args__ = (
        CheckConstraint("support_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_wellbeing_status'),
        UniqueConstraint('child_id', name='uq_wellbeing_child'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    support_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
    support_provider: Mapped[str | None] = mapped_column(String(160))
    last_followup_date: Mapped[date | None] = mapped_column(Date)
    next_followup_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    child = relationship('Child', back_populates='wellbeing')


class ChildProtectionRecord(TimestampMixin, Base):
    __tablename__ = 'child_protection_records'
    __table_args__ = (
        CheckConstraint("protection_status IN ('NO_ACTION_RECORDED', 'FOLLOW_UP_RECOMMENDED', 'SUPPORT_CONNECTED', 'REVIEW_REQUIRED')", name='ck_protection_status'),
        UniqueConstraint('child_id', name='uq_protection_child'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    protection_status: Mapped[str] = mapped_column(String(30), nullable=False, default='NO_ACTION_RECORDED')
    support_contact_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_review_date: Mapped[date | None] = mapped_column(Date)
    followup_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text)

    child = relationship('Child', back_populates='protection')


class InclusionRecord(TimestampMixin, Base):
    __tablename__ = 'inclusion_records'
    __table_args__ = (
        CheckConstraint("support_type IN ('ACCESSIBILITY', 'LEARNING_SUPPORT', 'MOBILITY_SUPPORT', 'COMMUNICATION_SUPPORT', 'OTHER')", name='ck_inclusion_type'),
        CheckConstraint("support_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_inclusion_status'),
        UniqueConstraint('child_id', name='uq_inclusion_child'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    requirement_present: Mapped[bool | None] = mapped_column(Boolean)
    support_type: Mapped[str] = mapped_column(String(30), nullable=False, default='OTHER')
    support_status: Mapped[str] = mapped_column(String(30), nullable=False, default='PENDING')
    notes: Mapped[str | None] = mapped_column(Text)

    child = relationship('Child', back_populates='inclusion')


class ServiceContinuityRecord(TimestampMixin, Base):
    __tablename__ = 'service_continuity_records'
    __table_args__ = (
        CheckConstraint("service_type IN ('EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION')", name='ck_continuity_service_type'),
        CheckConstraint("status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_REQUIRED', 'SUPPORT_NOT_REQUIRED', 'REVIEW_REQUIRED')", name='ck_continuity_status'),
        CheckConstraint(
            "confirmation_method IS NULL OR confirmation_method IN "
            "('FAMILY_REPORT', 'SERVICE_PROVIDER', 'DOCUMENT_REVIEW', 'IN_PERSON', 'OTHER')",
            name='ck_continuity_confirmation_method',
        ),
        CheckConstraint(
            "(status IN ('CONNECTED', 'SUPPORT_NOT_REQUIRED') "
            "AND outcome_confirmed_by_user_id IS NOT NULL "
            "AND outcome_confirmed_at IS NOT NULL AND confirmation_method IS NOT NULL) "
            "OR (status NOT IN ('CONNECTED', 'SUPPORT_NOT_REQUIRED') "
            "AND outcome_confirmed_by_user_id IS NULL AND outcome_confirmed_at IS NULL "
            "AND confirmation_method IS NULL AND supporting_reference IS NULL)",
            name='ck_continuity_outcome_evidence',
        ),
        Index('ix_continuity_child_migration', 'child_id', 'migration_id'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'), nullable=False)
    migration_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('migration_records.id', ondelete='RESTRICT'))
    service_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    action_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assigned_role: Mapped[str | None] = mapped_column(String(30))
    due_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    outcome_confirmed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'))
    outcome_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirmation_method: Mapped[str | None] = mapped_column(String(30))
    supporting_reference: Mapped[str | None] = mapped_column(String(200))

    child = relationship('Child', back_populates='continuity_records')
    migration = relationship('MigrationRecord', back_populates='continuity_records')
    outcome_confirmed_by = relationship('User')
    followups = relationship('FollowUpAction', back_populates='service_continuity', passive_deletes=True)


class FollowUpAction(TimestampMixin, Base):
    __tablename__ = 'follow_up_actions'
    __table_args__ = (
        CheckConstraint("status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')", name='ck_followups_status'),
        CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH')", name='ck_followups_priority'),
        CheckConstraint("assigned_role IS NULL OR assigned_role IN ('CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN')", name='ck_followups_assigned_role'),
        Index('ix_followups_family_status', 'family_id', 'status'),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('families.id', ondelete='RESTRICT'), nullable=False)
    child_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('children.id', ondelete='RESTRICT'))
    service_continuity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey('service_continuity_records.id', ondelete='RESTRICT'))
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='OPEN')
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default='MEDIUM')
    due_date: Mapped[date | None] = mapped_column(Date)
    assigned_role: Mapped[str | None] = mapped_column(String(30))

    service_continuity = relationship('ServiceContinuityRecord', back_populates='followups')