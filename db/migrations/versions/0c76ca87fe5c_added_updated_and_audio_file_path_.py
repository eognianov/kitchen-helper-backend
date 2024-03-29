"""added updated and audio_file_path fileds in instruction

Revision ID: 0c76ca87fe5c
Revises: f4950c999696
Create Date: 2024-01-24 09:42:08.266899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c76ca87fe5c'
down_revision: Union[str, None] = 'f4950c999696'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('RECIPE_INSTRUCTIONS', sa.Column('updated_by', sa.Integer(), nullable=True))
    op.add_column(
        'RECIPE_INSTRUCTIONS',
        sa.Column('updated_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.add_column('RECIPE_INSTRUCTIONS', sa.Column('audio_file', sa.String(length=500), nullable=True))
    op.create_foreign_key(None, 'RECIPE_INSTRUCTIONS', 'Users', ['updated_by'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'RECIPE_INSTRUCTIONS', type_='foreignkey')
    op.drop_column('RECIPE_INSTRUCTIONS', 'audio_file')
    op.drop_column('RECIPE_INSTRUCTIONS', 'updated_on')
    op.drop_column('RECIPE_INSTRUCTIONS', 'updated_by')
    # ### end Alembic commands ###
