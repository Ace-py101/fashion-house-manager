"""add email verification fields to users

Revision ID: b054d219cebf
Revises: 8155fc1e9615
Create Date: 2026-08-10 17:23:53.620225

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b054d219cebf"
down_revision = "8155fc1e9615"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "email_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )

        batch_op.add_column(
            sa.Column(
                "email_verified_at",
                sa.DateTime(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "email_verification_token_hash",
                sa.String(length=255),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "email_verification_token_expires_at",
                sa.DateTime(),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            None,
            ["email_verification_token_hash"]
        )

        batch_op.alter_column(
            "email_verified",
            server_default=None
        )


def downgrade():
    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            None,
            type_="unique"
        )

        batch_op.drop_column(
            "email_verification_token_expires_at"
        )

        batch_op.drop_column(
            "email_verification_token_hash"
        )

        batch_op.drop_column(
            "email_verified_at"
        )

        batch_op.drop_column(
            "email_verified"
        )
