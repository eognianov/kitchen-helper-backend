"""Add recipe and category

Revision ID: 0d117739f322
Revises:
Create Date: 2023-11-07 20:48:42.608800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d117739f322"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "RECIPE_CATEGORIES",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("created_by", sa.String(length=30), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.String(length=30), nullable=True),
        sa.Column(
            "updated_on",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "RECIPES",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("picture", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.String(length=1000), nullable=True),
        sa.Column("calories", sa.Float(), nullable=True),
        sa.Column("carbo", sa.Float(), nullable=True),
        sa.Column("fats", sa.Float(), nullable=True),
        sa.Column("proteins", sa.Float(), nullable=True),
        sa.Column("cholesterol", sa.Float(), nullable=True),
        sa.Column("time_to_prepare", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.String(length=30), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("updated_by", sa.String(length=30), nullable=True),
        sa.Column(
            "updated_on",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["RECIPE_CATEGORIES.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("RECIPES")
    op.drop_table("RECIPE_CATEGORIES")
    # ### end Alembic commands ###
