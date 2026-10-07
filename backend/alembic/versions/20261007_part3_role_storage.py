"""Align previously initialized user role storage with the ORM enum."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20261007_part3_role_storage'
down_revision = '20261007_part3_continuity'
branch_labels = None
depends_on = None


def _role_storage() -> tuple[str | None, str | None]:
    row = op.get_bind().execute(sa.text(
        "SELECT data_type, udt_name FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND table_name = 'users' AND column_name = 'role'"
    )).first()
    return (row[0], row[1]) if row else (None, None)


def upgrade() -> None:
    data_type, udt_name = _role_storage()
    if data_type == 'USER-DEFINED' and udt_name == 'user_role':
        return
    if data_type is None:
        raise RuntimeError('The Part 2 users.role column was not found.')

    user_role = postgresql.ENUM(
        'CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN',
        name='user_role',
        create_type=False,
    )
    user_role.create(op.get_bind(), checkfirst=True)
    op.execute('ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_role')
    op.execute('ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::text::user_role')


def downgrade() -> None:
    data_type, udt_name = _role_storage()
    if data_type != 'USER-DEFINED' or udt_name != 'user_role':
        return
    op.execute('ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(30) USING role::text')
    op.execute(
        "ALTER TABLE users ADD CONSTRAINT ck_users_role "
        "CHECK (role IN ('CITIZEN', 'SCHOOL', 'HEALTHCARE', 'NGO_WORKER', 'GOVERNMENT', 'ADMIN'))"
    )