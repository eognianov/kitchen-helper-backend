"""Recipes feature business logic"""
import db.connection
from .models import RecipeCategory, Recipe
from typing import Type


def get_all_recipe_categories() -> list[Type[RecipeCategory]]:
    """
    Get all recipe categories
    :return:
    """
    with db.connection.get_session() as session:
        return session.query(RecipeCategory).all()
