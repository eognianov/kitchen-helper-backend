"""add ingredient model

Revision ID: 6f16aa3da54c
Revises: 221bb1f84e86
Create Date: 2024-01-05 10:20:42.559858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f16aa3da54c'
down_revision: Union[str, None] = '221bb1f84e86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'INGREDIENTS',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('calories', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('carbo', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('fats', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('protein', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('cholesterol', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('measurement', sa.String(length=25), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('deleted_on', sa.DateTime(), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['created_by'],
            ['Users.id'],
        ),
        sa.ForeignKeyConstraint(
            ['deleted_by'],
            ['Users.id'],
        ),
        sa.ForeignKeyConstraint(
            ['updated_by'],
            ['Users.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_INGREDIENTS_name'), 'INGREDIENTS', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_INGREDIENTS_name'), table_name='INGREDIENTS')
    op.drop_table('INGREDIENTS')
    # ### end Alembic commands ###
