"""add recipe ingredient relation

Revision ID: f4950c999696
Revises: 53eaad816d48
Create Date: 2024-01-11 19:59:12.725943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4950c999696'
down_revision: Union[str, None] = '53eaad816d48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'RECIPE_INGREDIENTS_MAPPING',
        sa.Column('recipe_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.ForeignKeyConstraint(
            ['ingredient_id'],
            ['INGREDIENTS.id'],
        ),
        sa.ForeignKeyConstraint(
            ['recipe_id'],
            ['RECIPES.id'],
        ),
        sa.PrimaryKeyConstraint('recipe_id', 'ingredient_id'),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('RECIPE_INGREDIENTS_MAPPING')
    # ### end Alembic commands ###