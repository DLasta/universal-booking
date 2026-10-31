
"""Add organization model

Revision ID: 4045a6b8e4e7
Revises: 9808d99012d0
Create Date: 2026-10-30 14:38:16.426970

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4045a6b8e4e7"
down_revision = "9808d99012d0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("business_type", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("organization_id", sa.Integer(), nullable=True)
        )

        batch_op.create_index(
            "ix_users_organization_id",
            ["organization_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_users_organization_id_organizations",
            "organizations",
            ["organization_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_users_organization_id_organizations",
            type_="foreignkey",
        )

        batch_op.drop_index("ix_users_organization_id")
        batch_op.drop_column("organization_id")

    op.drop_table("organizations")
