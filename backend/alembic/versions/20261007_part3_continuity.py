"""Add family, child, and continuity records for Part 3."""

from alembic import op
import sqlalchemy as sa

revision = '20261007_part3_continuity'
down_revision = '20261007_initial_users'
branch_labels = None
depends_on = None

UUID = sa.Uuid(as_uuid=True)
TIMESTAMP = sa.DateTime(timezone=True)


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column('created_at', TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    ]


def upgrade() -> None:
    op.create_table(
        'families',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('family_reference_id', sa.String(24), nullable=False, unique=True),
        sa.Column('primary_guardian_user_id', UUID, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('family_name', sa.String(120), nullable=False),
        sa.Column('contact_mobile', sa.String(30), nullable=False),
        sa.Column('current_district', sa.String(100), nullable=False),
        sa.Column('current_taluka', sa.String(100), nullable=False),
        sa.Column('current_village_or_city', sa.String(120), nullable=False),
        sa.Column('current_address', sa.String(300)),
        sa.Column('preferred_language', sa.String(30), nullable=False, server_default='English'),
        *_timestamps(),
    )
    op.create_index('ix_families_family_reference_id', 'families', ['family_reference_id'], unique=True)
    op.create_index('ix_families_primary_guardian_user_id', 'families', ['primary_guardian_user_id'])

    op.create_table(
        'children',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('family_id', UUID, sa.ForeignKey('families.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('first_name', sa.String(80), nullable=False),
        sa.Column('last_name', sa.String(80), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(20), nullable=False, server_default='UNDISCLOSED'),
        sa.Column('education_status', sa.String(20), nullable=False, server_default='UNKNOWN'),
        sa.Column('current_class', sa.String(30)),
        sa.Column('preferred_language', sa.String(30), nullable=False, server_default='English'),
        sa.Column('disability_or_inclusion_requirement', sa.String(500)),
        *_timestamps(),
        sa.CheckConstraint("gender IN ('FEMALE', 'MALE', 'NON_BINARY', 'UNDISCLOSED')", name='ck_children_gender'),
        sa.CheckConstraint("education_status IN ('ENROLLED', 'PENDING', 'NOT_ENROLLED', 'UNKNOWN')", name='ck_children_education_status'),
    )
    op.create_index('ix_children_family_id', 'children', ['family_id'])

    op.create_table(
        'family_members',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('family_id', UUID, sa.ForeignKey('families.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='RESTRICT')),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT')),
        sa.Column('relationship_type', sa.String(20), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("relationship_type IN ('GUARDIAN', 'PARENT', 'CHILD')", name='ck_family_members_relationship'),
        sa.CheckConstraint('(user_id IS NOT NULL AND child_id IS NULL) OR (user_id IS NULL AND child_id IS NOT NULL)', name='ck_family_members_subject'),
        sa.UniqueConstraint('family_id', 'user_id', name='uq_family_member_user'),
    )
    op.create_index('ix_family_members_family_id', 'family_members', ['family_id'])

    op.create_table(
        'family_access',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('family_id', UUID, sa.ForeignKey('families.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('access_role', sa.String(20), nullable=False),
        sa.Column('granted_by_user_id', UUID, sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("access_role IN ('SCHOOL', 'HEALTHCARE', 'NGO_WORKER')", name='ck_family_access_role'),
        sa.UniqueConstraint('family_id', 'user_id', name='uq_family_access_user'),
    )
    op.create_index('ix_family_access_family_id', 'family_access', ['family_id'])
    op.create_index('ix_family_access_user_id', 'family_access', ['user_id'])

    op.create_table(
        'migration_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('family_id', UUID, sa.ForeignKey('families.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('from_district', sa.String(100), nullable=False),
        sa.Column('from_taluka', sa.String(100), nullable=False),
        sa.Column('from_location', sa.String(120), nullable=False),
        sa.Column('to_district', sa.String(100), nullable=False),
        sa.Column('to_taluka', sa.String(100), nullable=False),
        sa.Column('to_location', sa.String(120), nullable=False),
        sa.Column('migration_date', sa.Date(), nullable=False),
        sa.Column('migration_reason', sa.String(300)),
        sa.Column('status', sa.String(20), nullable=False, server_default='ACTIVE'),
        *_timestamps(),
        sa.CheckConstraint("status IN ('PLANNED', 'ACTIVE', 'COMPLETED')", name='ck_migrations_status'),
    )
    op.create_index('ix_migration_records_family_id', 'migration_records', ['family_id'])

    service_columns = _timestamps()
    op.create_table(
        'education_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('previous_school_name', sa.String(160)),
        sa.Column('previous_school_location', sa.String(160)),
        sa.Column('current_school_name', sa.String(160)),
        sa.Column('current_school_location', sa.String(160)),
        sa.Column('current_class', sa.String(30)),
        sa.Column('enrollment_status', sa.String(20), nullable=False, server_default='UNKNOWN'),
        sa.Column('transfer_status', sa.String(20), nullable=False, server_default='NOT_STARTED'),
        sa.Column('last_attendance_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("enrollment_status IN ('ENROLLED', 'PENDING', 'NOT_ENROLLED', 'UNKNOWN')", name='ck_education_enrollment'),
        sa.CheckConstraint("transfer_status IN ('COMPLETED', 'PENDING', 'NOT_STARTED', 'NOT_REQUIRED')", name='ck_education_transfer'),
    )
    op.create_table(
        'healthcare_continuity',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('healthcare_provider_name', sa.String(160)),
        sa.Column('healthcare_location', sa.String(160)),
        sa.Column('continuity_status', sa.String(30), nullable=False, server_default='PENDING'),
        sa.Column('last_followup_date', sa.Date()),
        sa.Column('next_followup_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("continuity_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_healthcare_status'),
    )
    op.create_table(
        'nutrition_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('nutrition_service_name', sa.String(160)),
        sa.Column('nutrition_service_location', sa.String(160)),
        sa.Column('service_status', sa.String(30), nullable=False, server_default='PENDING'),
        sa.Column('last_service_date', sa.Date()),
        sa.Column('next_service_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("service_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_nutrition_status'),
    )
    op.create_table(
        'wellbeing_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('support_status', sa.String(30), nullable=False, server_default='PENDING'),
        sa.Column('support_provider', sa.String(160)),
        sa.Column('last_followup_date', sa.Date()),
        sa.Column('next_followup_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("support_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_wellbeing_status'),
    )
    op.create_table(
        'child_protection_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('protection_status', sa.String(30), nullable=False, server_default='NO_ACTION_RECORDED'),
        sa.Column('support_contact_available', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('last_review_date', sa.Date()),
        sa.Column('followup_required', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("protection_status IN ('NO_ACTION_RECORDED', 'FOLLOW_UP_RECOMMENDED', 'SUPPORT_CONNECTED', 'REVIEW_REQUIRED')", name='ck_protection_status'),
    )
    op.create_table(
        'inclusion_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('requirement_present', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('support_type', sa.String(30), nullable=False, server_default='OTHER'),
        sa.Column('support_status', sa.String(30), nullable=False, server_default='PENDING'),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("support_type IN ('ACCESSIBILITY', 'LEARNING_SUPPORT', 'MOBILITY_SUPPORT', 'COMMUNICATION_SUPPORT', 'OTHER')", name='ck_inclusion_type'),
        sa.CheckConstraint("support_status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')", name='ck_inclusion_status'),
    )

    op.create_table(
        'service_continuity_records',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('migration_id', UUID, sa.ForeignKey('migration_records.id', ondelete='RESTRICT')),
        sa.Column('service_type', sa.String(30), nullable=False),
        sa.Column('status', sa.String(30), nullable=False),
        sa.Column('action_required', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('assigned_role', sa.String(30)),
        sa.Column('due_date', sa.Date()),
        sa.Column('notes', sa.Text()),
        *_timestamps(),
        sa.CheckConstraint("service_type IN ('EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION')", name='ck_continuity_service_type'),
        sa.CheckConstraint("status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE', 'REVIEW_REQUIRED')", name='ck_continuity_status'),
    )
    op.create_index('ix_service_continuity_child_migration', 'service_continuity_records', ['child_id', 'migration_id'])

    op.create_table(
        'follow_up_actions',
        sa.Column('id', UUID, primary_key=True, nullable=False),
        sa.Column('family_id', UUID, sa.ForeignKey('families.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('child_id', UUID, sa.ForeignKey('children.id', ondelete='RESTRICT')),
        sa.Column('service_continuity_id', UUID, sa.ForeignKey('service_continuity_records.id', ondelete='RESTRICT')),
        sa.Column('title', sa.String(160), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(20), nullable=False, server_default='OPEN'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='MEDIUM'),
        sa.Column('due_date', sa.Date()),
        sa.Column('assigned_role', sa.String(30)),
        *_timestamps(),
        sa.CheckConstraint("status IN ('OPEN', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')", name='ck_followups_status'),
        sa.CheckConstraint("priority IN ('LOW', 'MEDIUM', 'HIGH')", name='ck_followups_priority'),
        sa.CheckConstraint("assigned_role IS NULL OR assigned_role IN ('CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN')", name='ck_followups_assigned_role'),
    )
    op.create_index('ix_follow_up_actions_family_status', 'follow_up_actions', ['family_id', 'status'])


def downgrade() -> None:
    op.drop_index('ix_follow_up_actions_family_status', table_name='follow_up_actions')
    op.drop_table('follow_up_actions')
    op.drop_index('ix_service_continuity_child_migration', table_name='service_continuity_records')
    op.drop_table('service_continuity_records')
    op.drop_table('inclusion_records')
    op.drop_table('child_protection_records')
    op.drop_table('wellbeing_records')
    op.drop_table('nutrition_records')
    op.drop_table('healthcare_continuity')
    op.drop_table('education_records')
    op.drop_index('ix_migration_records_family_id', table_name='migration_records')
    op.drop_table('migration_records')
    op.drop_index('ix_family_access_user_id', table_name='family_access')
    op.drop_index('ix_family_access_family_id', table_name='family_access')
    op.drop_table('family_access')
    op.drop_index('ix_family_members_family_id', table_name='family_members')
    op.drop_table('family_members')
    op.drop_index('ix_children_family_id', table_name='children')
    op.drop_table('children')
    op.drop_index('ix_families_primary_guardian_user_id', table_name='families')
    op.drop_index('ix_families_family_reference_id', table_name='families')
    op.drop_table('families')