"""Add fulfillment type to orders

Revision ID: 06740edd1708
Revises: 99a9db8adf05
Create Date: 2026-08-02 13:37:03.195477
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "06740edd1708"
down_revision = "99a9db8adf05"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("customer_history", schema=None) as batch_op:
        batch_op.alter_column(
            "action",
            existing_type=sa.VARCHAR(length=100),
            nullable=False
        )

    with op.batch_alter_table("order_history", schema=None) as batch_op:
        batch_op.alter_column(
            "action",
            existing_type=sa.VARCHAR(length=100),
            nullable=False
        )

    with op.batch_alter_table("orders", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "fulfillment_type",
                sa.String(length=50),
                nullable=False,
                server_default="custom"
            )
        )

        batch_op.add_column(
            sa.Column(
                "delivered_at",
                sa.DateTime(),
                nullable=True
            )
        )

        batch_op.alter_column(
            "order_type",
            existing_type=sa.VARCHAR(length=50),
            nullable=False
        )

        batch_op.alter_column(
            "fulfillment_type",
            server_default=None
        )


def downgrade():

    with op.batch_alter_table("orders", schema=None) as batch_op:

        batch_op.drop_column("delivered_at")
        batch_op.drop_column("fulfillment_type")

        batch_op.alter_column(
            "order_type",
            existing_type=sa.VARCHAR(length=50),
            nullable=True
        )

    with op.batch_alter_table("order_history", schema=None) as batch_op:
        batch_op.alter_column(
            "action",
            existing_type=sa.VARCHAR(length=100),
            nullable=True
        )

    with op.batch_alter_table("customer_history", schema=None) as batch_op:
        batch_op.alter_column(
            "action",
            existing_type=sa.VARCHAR(length=100),
            nullable=True
        )
