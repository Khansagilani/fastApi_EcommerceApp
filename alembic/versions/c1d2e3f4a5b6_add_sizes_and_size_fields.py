"""add sizes to products and size to cart_items

Revision ID: c1d2e3f4a5b6
Revises: b8c45e8bd806
Create Date: 2026-05-24 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'b8c45e8bd806'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column(
        'sizes', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('cart_items', sa.Column(
        'size', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('products', 'sizes')
    op.drop_column('cart_items', 'size')
