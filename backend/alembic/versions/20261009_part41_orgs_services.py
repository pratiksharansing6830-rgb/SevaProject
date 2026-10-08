"""Part 4.1: organizations and services directory tables."""

from alembic import op
import sqlalchemy as sa

revision = '20261009_part41_orgs_services'
down_revision = '20261008_continuity_reason_and_location'
branch_labels = None
depends_on = None

ORG_TYPES = (
    "'SCHOOL', 'HEALTHCARE', 'NGO', 'GOVERNMENT', 'NUTRITION_CENTER', 'CHILD_SUPPORT', "
    "'WELLBEING_SUPPORT', 'DISABILITY_SUPPORT', 'COMMUNITY_SERVICE', 'OTHER'"
)
SERVICE_TYPES = (
    "'EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION', "
    "'GOVERNMENT_SCHEME', 'SOCIAL_SUPPORT', 'DOCUMENTATION', 'HOUSING_SUPPORT', 'OTHER'"
)


def upgrade() -> None:
    op.create_table(
        'organizations',
        sa.Column('id', sa.Uuid(), primary_key=True, nullable=False),
        sa.Column('organization_name', sa.String(200), nullable=False),
        sa.Column('organization_type', sa.String(30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contact_phone', sa.String(30), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(300), nullable=True),
        sa.Column('address', sa.String(300), nullable=True),
        sa.Column('district', sa.String(100), nullable=True),
        sa.Column('taluka', sa.String(100), nullable=True),
        sa.Column('city_or_village', sa.String(120), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f'organization_type IN ({ORG_TYPES})', name='ck_organizations_type'),
        sa.CheckConstraint('latitude IS NULL OR (latitude >= -90 AND latitude <= 90)', name='ck_organizations_latitude'),
        sa.CheckConstraint('longitude IS NULL OR (longitude >= -180 AND longitude <= 180)', name='ck_organizations_longitude'),
    )
    op.create_index('ix_organizations_organization_type', 'organizations', ['organization_type'])
    op.create_index('ix_organizations_district_taluka', 'organizations', ['district', 'taluka'])

    op.create_table(
        'services',
        sa.Column('id', sa.Uuid(), primary_key=True, nullable=False),
        sa.Column('organization_id', sa.Uuid(), sa.ForeignKey('organizations.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('service_name', sa.String(160), nullable=False),
        sa.Column('service_type', sa.String(30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('eligibility', sa.Text(), nullable=True),
        sa.Column('contact_information', sa.String(300), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(f'service_type IN ({SERVICE_TYPES})', name='ck_services_type'),
    )
    op.create_index('ix_services_service_type', 'services', ['service_type'])
    op.create_index('ix_services_org_active', 'services', ['organization_id', 'is_active'])


def downgrade() -> None:
    op.drop_index('ix_services_org_active', table_name='services')
    op.drop_index('ix_services_service_type', table_name='services')
    op.drop_table('services')
    op.drop_index('ix_organizations_district_taluka', table_name='organizations')
    op.drop_index('ix_organizations_organization_type', table_name='organizations')
    op.drop_table('organizations')