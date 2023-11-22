"""created token model added field to user model

Revision ID: cfcb1c535326
Revises: ef1413eb13d9
Create Date: 2023-11-22 15:01:50.126618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfcb1c535326'
down_revision: Union[str, None] = 'ef1413eb13d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TOKEN',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_confirmation_token', sa.String(length=43), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('expired_on', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['Users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email_confirmation_token')
    )
    op.add_column('Users', sa.Column('is_email_confirmed', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Users', 'is_email_confirmed')
    op.drop_table('TOKEN')
    # ### end Alembic commands ###
