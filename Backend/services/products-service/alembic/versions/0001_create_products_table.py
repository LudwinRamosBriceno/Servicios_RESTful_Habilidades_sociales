"""Create products table.

Revision ID: 0001_create_products_table
Revises:
Create Date: 2026-04-20 00:00:00

"""

import sqlalchemy as sa
from alembic import op

revision = "0001_create_products_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply schema changes for products."""
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Revert schema changes for products."""
    op.drop_table("products")
