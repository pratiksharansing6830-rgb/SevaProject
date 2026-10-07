"""Add continuity reasons and keep the family current location aligned to completed migrations."""

from alembic import op
import sqlalchemy as sa

revision = '20261008_continuity_reason_and_location'
down_revision = '20261007_part3_role_storage'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('service_continuity_records') as batch_op:
        batch_op.add_column(sa.Column('reason', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('service_continuity_records') as batch_op:
        batch_op.drop_column('reason')
