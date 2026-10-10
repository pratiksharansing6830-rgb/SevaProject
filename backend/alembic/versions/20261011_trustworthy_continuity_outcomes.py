"""Require recorded evidence for terminal continuity outcomes."""

from alembic import op
import sqlalchemy as sa

revision = '20261011_trustworthy_continuity_outcomes'
down_revision = '20261010_part44_child_support_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "UPDATE service_continuity_records SET status = 'PENDING', action_required = TRUE "
        "WHERE status = 'CONNECTED'"
    )
    with op.batch_alter_table('service_continuity_records') as batch_op:
        batch_op.drop_constraint('ck_continuity_status', type_='check')
        batch_op.create_check_constraint(
            'ck_continuity_status',
            "status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_REQUIRED', 'SUPPORT_NOT_REQUIRED', 'REVIEW_REQUIRED')",
        )
        batch_op.add_column(sa.Column(
            'outcome_confirmed_by_user_id',
            sa.Uuid(),
            nullable=True,
        ))
        batch_op.create_foreign_key(
            'fk_continuity_outcome_confirmed_by',
            'users',
            ['outcome_confirmed_by_user_id'],
            ['id'],
            ondelete='RESTRICT',
        )
        batch_op.add_column(sa.Column('outcome_confirmed_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('confirmation_method', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('supporting_reference', sa.String(200), nullable=True))
        batch_op.create_check_constraint(
            'ck_continuity_confirmation_method',
            "confirmation_method IS NULL OR confirmation_method IN "
            "('FAMILY_REPORT', 'SERVICE_PROVIDER', 'DOCUMENT_REVIEW', 'IN_PERSON', 'OTHER')",
        )
        batch_op.create_check_constraint(
            'ck_continuity_outcome_evidence',
            "(status IN ('CONNECTED', 'SUPPORT_NOT_REQUIRED') "
            "AND outcome_confirmed_by_user_id IS NOT NULL "
            "AND outcome_confirmed_at IS NOT NULL AND confirmation_method IS NOT NULL) "
            "OR (status NOT IN ('CONNECTED', 'SUPPORT_NOT_REQUIRED') "
            "AND outcome_confirmed_by_user_id IS NULL AND outcome_confirmed_at IS NULL "
            "AND confirmation_method IS NULL AND supporting_reference IS NULL)",
        )

    op.execute(
        "UPDATE service_continuity_records SET status = 'FOLLOW_UP_REQUIRED' "
        "WHERE status IN ('FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE')"
    )
    op.execute(
        "UPDATE service_continuity_records SET assigned_role = CASE service_type "
        "WHEN 'EDUCATION' THEN 'SCHOOL' WHEN 'HEALTHCARE' THEN 'HEALTHCARE' "
        "ELSE 'NGO_WORKER' END WHERE action_required = TRUE"
    )

    with op.batch_alter_table('inclusion_records') as batch_op:
        batch_op.alter_column(
            'requirement_present',
            existing_type=sa.Boolean(),
            nullable=True,
            server_default=None,
        )
    op.execute("UPDATE inclusion_records SET requirement_present = NULL WHERE requirement_present = FALSE")


def downgrade() -> None:
    op.execute(
        "UPDATE service_continuity_records SET status = 'PENDING', action_required = TRUE, "
        "outcome_confirmed_by_user_id = NULL, outcome_confirmed_at = NULL, "
        "confirmation_method = NULL, supporting_reference = NULL "
        "WHERE status IN ('CONNECTED', 'SUPPORT_NOT_REQUIRED')"
    )
    op.execute(
        "UPDATE service_continuity_records SET status = 'FOLLOW_UP_RECOMMENDED' "
        "WHERE status = 'FOLLOW_UP_REQUIRED'"
    )
    with op.batch_alter_table('service_continuity_records') as batch_op:
        batch_op.drop_constraint('ck_continuity_outcome_evidence', type_='check')
        batch_op.drop_constraint('ck_continuity_confirmation_method', type_='check')
        batch_op.drop_constraint('ck_continuity_status', type_='check')
        batch_op.create_check_constraint(
            'ck_continuity_status',
            "status IN ('CONNECTED', 'PENDING', 'FOLLOW_UP_RECOMMENDED', 'NOT_AVAILABLE', 'REVIEW_REQUIRED')",
        )
        batch_op.drop_constraint('fk_continuity_outcome_confirmed_by', type_='foreignkey')
        batch_op.drop_column('supporting_reference')
        batch_op.drop_column('confirmation_method')
        batch_op.drop_column('outcome_confirmed_at')
        batch_op.drop_column('outcome_confirmed_by_user_id')

    op.execute("UPDATE inclusion_records SET requirement_present = FALSE WHERE requirement_present IS NULL")
    with op.batch_alter_table('inclusion_records') as batch_op:
        batch_op.alter_column(
            'requirement_present',
            existing_type=sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        )
