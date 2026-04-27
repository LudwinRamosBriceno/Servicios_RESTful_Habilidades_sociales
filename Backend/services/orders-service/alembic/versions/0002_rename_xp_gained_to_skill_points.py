"""rename xp_gained to skill_points

Revision ID: 0002_skill_points
Revises: 0001_create_orders_table
Create Date: 2026-04-20 00:00:00

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "0002_skill_points"
down_revision = "0001_create_orders_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("orders", "xp_gained", new_column_name="skill_points")


def downgrade() -> None:
    op.alter_column("orders", "skill_points", new_column_name="xp_gained")