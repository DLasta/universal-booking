
"""Add user roles

Revision ID: 4238bd1700ca
Revises: 4045a6b8e4e7
Create Date: 2026-10-31 19:55:34.608915

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4238bd1700ca"
down_revision = "4045a6b8e4e7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="owner",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade():
    op.drop_column("users", "role")
