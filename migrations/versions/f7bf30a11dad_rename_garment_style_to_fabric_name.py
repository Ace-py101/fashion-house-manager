"""Rename garment_style to fabric_name

Revision ID: f7bf30a11dad
Revises: f7e0a8ed6242
Create Date: 2026-08-04 13:17:43.409935

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "f7bf30a11dad"
down_revision = "f7e0a8ed6242"
branch_labels = None
depends_on = None


def upgrade():

    op.alter_column(
        "orders",
        "garment_style",
        new_column_name="fabric_name"
    )


def downgrade():

    op.alter_column(
        "orders",
        "fabric_name",
        new_column_name="garment_style"
    )
