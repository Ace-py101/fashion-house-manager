"""Update style metadata fields

Revision ID: 7b857e5a1c2e
Revises: ea2c14b03637
Create Date: 2026-08-10 00:18:33.727821
"""

from alembic import op
import sqlalchemy as sa


revision = "7b857e5a1c2e"
down_revision = "ea2c14b03637"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "styles",
        schema=None
    ) as batch_op:

        # Preserve existing style codes by
        # turning style_code into style_id.
        batch_op.alter_column(
            "style_code",
            new_column_name="style_id"
        )

        # Add the new metadata fields temporarily
        # as nullable so existing records survive.
        batch_op.add_column(
            sa.Column(
                "style_type",
                sa.String(length=50),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "occasion_fit",
                sa.String(length=80),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "garment_name",
                sa.String(length=80),
                nullable=True
            )
        )

    # Populate the new fields from the existing data.
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE styles
            SET style_type = 'Custom Made'
            WHERE style_type IS NULL
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE styles
            SET occasion_fit = COALESCE(category, 'Other')
            WHERE occasion_fit IS NULL
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE styles
            SET garment_name = COALESCE(
                garment_type,
                'Other'
            )
            WHERE garment_name IS NULL
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE styles
            SET fabric_requirement = ''
            WHERE fabric_requirement IS NULL
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE styles
            SET status = 'Active'
            WHERE status IS NULL
            """
        )
    )

    with op.batch_alter_table(
        "styles",
        schema=None
    ) as batch_op:

        # Remove the old style_code index.
        batch_op.drop_index(
            batch_op.f("ix_styles_style_code")
        )

        # Make the new fields required.
        batch_op.alter_column(
            "style_type",
            existing_type=sa.String(length=50),
            nullable=False
        )

        batch_op.alter_column(
            "occasion_fit",
            existing_type=sa.String(length=80),
            nullable=False
        )

        batch_op.alter_column(
            "garment_name",
            existing_type=sa.String(length=80),
            nullable=False
        )

        batch_op.alter_column(
            "fabric_requirement",
            existing_type=sa.VARCHAR(length=120),
            nullable=False
        )

        batch_op.alter_column(
            "status",
            existing_type=sa.VARCHAR(length=20),
            nullable=False
        )

        # Create the new unique style identifier index.
        batch_op.create_index(
            batch_op.f("ix_styles_style_id"),
            ["style_id"],
            unique=True
        )

        # Remove metadata that is no longer part
        # of the current Style model.
        batch_op.drop_column("category")
        batch_op.drop_column("garment_type")
        batch_op.drop_column("difficulty")
        batch_op.drop_column("estimated_days")
        batch_op.drop_column("description")
        batch_op.drop_column("tags")
        batch_op.drop_column("reference_source")
        batch_op.drop_column("reference_url")
        batch_op.drop_column("collection")
        batch_op.drop_column("designer")
        batch_op.drop_column("season")
        batch_op.drop_column("occasion")
        batch_op.drop_column("price_estimate")
        batch_op.drop_column("primary_colour")
        batch_op.drop_column("secondary_colour")
        batch_op.drop_column("notes")


def downgrade():

    raise RuntimeError(
        "Downgrade is intentionally disabled for "
        "the style metadata migration."
    )
