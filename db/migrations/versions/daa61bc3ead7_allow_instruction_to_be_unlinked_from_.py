"""allow instruction to be unlinked from recipe

Revision ID: daa61bc3ead7
Revises: 3eac26f37e69
Create Date: 2024-01-10 19:27:22.253580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daa61bc3ead7'
down_revision: Union[str, None] = '3eac26f37e69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('RECIPE_INSTRUCTIONS', 'recipe_id', existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('RECIPE_INSTRUCTIONS', 'recipe_id', existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###
