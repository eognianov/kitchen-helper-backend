"""Merge recipe and users migrations

Revision ID: 663d0c834556
Revises: 0d117739f322, df52ec2ba937
Create Date: 2023-11-10 16:33:02.711605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "663d0c834556"
down_revision: Union[str, None] = ("0d117739f322", "df52ec2ba937")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
