"""add_ingredients_models

Revision ID: 86b5bc90e306
Revises: 39b0a24527e0
Create Date: 2023-12-13 09:46:55.874521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86b5bc90e306'
down_revision: Union[str, None] = '39b0a24527e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('INGREDIENTS', 'measurement',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Enum('KG', 'ML', 'G', 'L', 'OZ', 'LB', 'CUP', name='measurementunits'),
               existing_nullable=False,
                    postgresql_using="measurement::text::measurementunits")
    op.alter_column('INGREDIENTS', 'deleted_by',
               existing_type=sa.VARCHAR(),
               type_=sa.Integer(),
               existing_nullable=True,
                    postgresql_using="deleted_by::integer")
    op.create_foreign_key(None, 'INGREDIENTS', 'Users', ['deleted_by'], ['id'])
    op.alter_column('INGREDIENT_CATEGORIES', 'name',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=255),
               existing_nullable=False)
    op.alter_column('INGREDIENT_CATEGORIES', 'created_by',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.Integer(),
               existing_nullable=False,
                    postgresql_using="created_by::integer")
    op.alter_column('INGREDIENT_CATEGORIES', 'updated_by',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.Integer(),
               existing_nullable=True,
                    postgresql_using="updated_by::integer")
    op.create_foreign_key(None, 'INGREDIENT_CATEGORIES', 'Users', ['updated_by'], ['id'])
    op.create_foreign_key(None, 'INGREDIENT_CATEGORIES', 'Users', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'INGREDIENT_CATEGORIES', type_='foreignkey')
    op.drop_constraint(None, 'INGREDIENT_CATEGORIES', type_='foreignkey')
    op.alter_column('INGREDIENT_CATEGORIES', 'updated_by',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=30),
               existing_nullable=True)
    op.alter_column('INGREDIENT_CATEGORIES', 'created_by',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    op.alter_column('INGREDIENT_CATEGORIES', 'name',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
    op.drop_constraint(None, 'INGREDIENTS', type_='foreignkey')
    op.alter_column('INGREDIENTS', 'deleted_by',
               existing_type=sa.Integer(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    op.alter_column('INGREDIENTS', 'measurement',
               existing_type=sa.Enum('KG', 'ML', 'G', 'L', 'OZ', 'LB', 'CUP', name='measurementunits'),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=False)
    # ### end Alembic commands ###
