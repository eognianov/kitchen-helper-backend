"""delete picture field, added serves field

Revision ID: a7676f686dae
Revises: 6f16aa3da54c
Create Date: 2024-01-09 12:33:50.231008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7676f686dae'
down_revision: Union[str, None] = '6f16aa3da54c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('RECIPES', sa.Column('serves', sa.Integer(), nullable=False, server_default='1'))
    op.drop_column('RECIPES', 'picture')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('RECIPES', sa.Column('picture', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('RECIPES', 'serves')
    # ### end Alembic commands ###
