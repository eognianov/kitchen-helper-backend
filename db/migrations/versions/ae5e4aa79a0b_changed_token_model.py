"""changed token model

Revision ID: ae5e4aa79a0b
Revises: ceb7b1ed32c6
Create Date: 2023-11-29 13:47:00.536917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae5e4aa79a0b'
down_revision: Union[str, None] = 'ceb7b1ed32c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
