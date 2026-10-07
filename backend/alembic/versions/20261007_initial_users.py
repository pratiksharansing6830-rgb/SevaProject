from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20261007_initial_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = postgresql.ENUM(
        'CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN',
        name='user_role',
        create_type=False,
    )
    user_role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('full_name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('mobile_number', sa.String(length=30), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', user_role, nullable=False),
        sa.Column('preferred_language', sa.String(length=30), nullable=False, server_default='English'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('mobile_number', name='uq_users_mobile_number'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_mobile_number'), 'users', ['mobile_number'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_mobile_number'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    postgresql.ENUM(name='user_role').drop(op.get_bind(), checkfirst=True)
