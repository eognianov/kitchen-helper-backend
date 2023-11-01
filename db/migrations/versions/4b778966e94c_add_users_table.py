"""Add Users Table

Revision ID: 4b778966e94c
Revises: 
Create Date: 2023-11-01 20:12:40.760913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4b778966e94c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(length=30), nullable=False),
                    sa.Column('email', sa.String(length=50), nullable=False),
                    sa.Column('password', sa.LargeBinary(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'),
                    sa.UniqueConstraint('username')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Users')
    # ### end Alembic commands ###
