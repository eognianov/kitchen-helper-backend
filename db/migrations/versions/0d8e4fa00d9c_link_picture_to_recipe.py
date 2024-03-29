"""link picture to recipe

Revision ID: 0d8e4fa00d9c
Revises: a7676f686dae
Create Date: 2024-01-09 12:34:32.456090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d8e4fa00d9c'
down_revision: Union[str, None] = 'a7676f686dae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('RECIPES', sa.Column('picture', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'RECIPES', 'IMAGES', ['picture'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'RECIPES', type_='foreignkey')
    op.drop_column('RECIPES', 'picture')
    # ### end Alembic commands ###
