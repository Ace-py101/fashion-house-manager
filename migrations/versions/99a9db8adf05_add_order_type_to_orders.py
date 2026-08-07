from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "99a9db8adf05"
down_revision = "0699576f7cb5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "order_type",
                sa.String(length=50),
                nullable=True
            )
        )


def downgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_column("order_type")
