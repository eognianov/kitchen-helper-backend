"""remove-created-by-string-columns

Revision ID: 78a3e103b080
Revises: 97b56ec45dfa
Create Date: 2023-12-11 20:01:42.955207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "78a3e103b080"
down_revision: Union[str, None] = "97b56ec45dfa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("Roles", "created_by")
    op.drop_column("user_roles", "added_by")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "user_roles",
        sa.Column(
            "added_by", sa.VARCHAR(length=50), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "Roles",
        sa.Column(
            "created_by", sa.VARCHAR(length=30), autoincrement=False, nullable=True
        ),
    )
    # ### end Alembic commands ###
