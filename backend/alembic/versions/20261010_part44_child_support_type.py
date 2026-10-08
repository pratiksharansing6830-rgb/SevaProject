"""Part 4.4: allow CHILD_SUPPORT as a service type."""

from alembic import op

revision = '20261010_part44_child_support_type'
down_revision = '20261009_part41_orgs_services'
branch_labels = None
depends_on = None

OLD_TYPES = (
    "'EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'WELLBEING', 'INCLUSION', "
    "'GOVERNMENT_SCHEME', 'SOCIAL_SUPPORT', 'DOCUMENTATION', 'HOUSING_SUPPORT', 'OTHER'"
)
NEW_TYPES = (
    "'EDUCATION', 'HEALTHCARE', 'NUTRITION', 'PROTECTION', 'CHILD_SUPPORT', 'WELLBEING', 'INCLUSION', "
    "'GOVERNMENT_SCHEME', 'SOCIAL_SUPPORT', 'DOCUMENTATION', 'HOUSING_SUPPORT', 'OTHER'"
)


def upgrade() -> None:
    op.drop_constraint('ck_services_type', 'services', type_='check')
    op.create_check_constraint('ck_services_type', 'services', f'service_type IN ({NEW_TYPES})')


def downgrade() -> None:
    op.execute("UPDATE services SET service_type = 'PROTECTION' WHERE service_type = 'CHILD_SUPPORT'")
    op.drop_constraint('ck_services_type', 'services', type_='check')
    op.create_check_constraint('ck_services_type', 'services', f'service_type IN ({OLD_TYPES})')