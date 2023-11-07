"""Recipes feature business logic"""
import db.connection
from .models import RecipeCategory, Recipe
from .exceptions import CategoryNotFoundException
from typing import Type
from sqlalchemy import update


def get_all_recipe_categories() -> list[Type[RecipeCategory]]:
    """
    Get all recipe categories
    :return:
    """
    with db.connection.get_session() as session:
        return session.query(RecipeCategory).all()


def get_category_by_id(category_id: int) -> Type[RecipeCategory]:
    """
    Get category by id

    :param category_id:
    :return:
    """

    with db.connection.get_session() as session:
        category = session.query(RecipeCategory).where(RecipeCategory.id == category_id).first()
        if not category:
            raise CategoryNotFoundException()
        return category


def update_category(category_id: int, field: str, value: str, updated_by: str = 'me') -> Type[RecipeCategory]:
    category = get_category_by_id(category_id)
    with db.connection.get_session() as session:
        session.execute(update(RecipeCategory), [{"id": category.id, f"{field}": value, "updated_by": updated_by}])
        session.commit()
        return session.query(RecipeCategory).where(RecipeCategory.id == category_id).first()