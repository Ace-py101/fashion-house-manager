"""Add phone verification fields

Revision ID: 1407b4291493
Revises: 64df9bc25d5a
Create Date: 2026-08-12 16:56:03.514348

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1407b4291493"
down_revision = "64df9bc25d5a"
branch_labels = None
depends_on = None


def upgrade():

    # ============================================================
    # PHONE VERIFICATION FIELDS
    #
    # Existing users already exist in the database.
    #
    # phone_number and the verification timestamps/hashes can
    # safely be nullable because existing accounts have not gone
    # through phone verification yet.
    #
    # phone_verified is temporarily nullable so PostgreSQL can
    # add the column to the existing users table safely.
    # ============================================================

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "phone_number",
                sa.String(length=30),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "phone_verified",
                sa.Boolean(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "phone_verified_at",
                sa.DateTime(),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "phone_verification_code_hash",
                sa.String(length=255),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "phone_verification_code_expires_at",
                sa.DateTime(),
                nullable=True
            )
        )


    # ============================================================
    # INITIALIZE EXISTING ACCOUNTS
    #
    # The previous batch operation has now completed, so the
    # phone_verified column definitely exists in PostgreSQL.
    #
    # Existing accounts begin with an unverified phone state.
    # ============================================================

    op.execute(
        "UPDATE users "
        "SET phone_verified = FALSE "
        "WHERE phone_verified IS NULL"
    )


    # ============================================================
    # ENFORCE PRODUCTION CONSTRAINT
    #
    # Every user must have an explicit phone verification state.
    # ============================================================

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.alter_column(
            "phone_verified",
            existing_type=sa.Boolean(),
            nullable=False
        )


    # ============================================================
    # PHONE NUMBER INDEX
    #
    # PostgreSQL allows multiple NULL values in a unique index,
    # which is exactly what we need for existing accounts that
    # have not supplied a phone number yet.
    # ============================================================

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.create_index(
            batch_op.f("ix_users_phone_number"),
            ["phone_number"],
            unique=True
        )


def downgrade():

    # ============================================================
    # REMOVE PHONE VERIFICATION FIELDS
    # ============================================================

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.drop_index(
            batch_op.f("ix_users_phone_number")
        )

        batch_op.drop_column(
            "phone_verification_code_expires_at"
        )

        batch_op.drop_column(
            "phone_verification_code_hash"
        )

        batch_op.drop_column(
            "phone_verified_at"
        )

        batch_op.drop_column(
            "phone_verified"
        )

        batch_op.drop_column(
            "phone_number"
        )
