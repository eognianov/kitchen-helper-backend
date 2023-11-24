"""Recipes feature business logic"""
from fastapi import HTTPException

import db.connection
from .models import RecipeCategory, Recipe
from .exceptions import CategoryNotFoundException, CategoryNameViolationException, RecipeNotFoundException
from typing import Type
from sqlalchemy import update, and_
import sqlalchemy.exc
from datetime import datetime

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
    """Update category"""
    category = get_category_by_id(category_id)
    try:
        with db.connection.get_session() as session:
            session.execute(update(RecipeCategory), [{"id": category.id, f"{field}": value, "updated_by": updated_by}])
            session.commit()
            RecipeCategory.__setattr__(category, field, value)
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise CategoryNameViolationException(ex)


def create_category(category_name: str, created_by: str = 'me') -> RecipeCategory:
    """Create category"""

    try:
        category = RecipeCategory(name=category_name, created_by=created_by)
        with db.connection.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise CategoryNameViolationException(ex)


def create_recipe(*, name: str, time_to_prepare: int, category_id: int = None, picture: str = None, summary: str = None,
                  calories: float = 0, carbo: float = 0, fats: float = 0, proteins: float = 0, cholesterol: float = 0, created_by: str = 'me'):
    """
    Create recipe

    :param name:
    :param time_to_prepare:
    :param category_id:
    :param picture:
    :param summary:
    :param calories:
    :param carbo:
    :param fats:
    :param proteins:
    :param cholesterol:
    :param created_by:
    :return:
    """

    category = None
    if category_id:
        category = get_category_by_id(category_id)

    recipe = Recipe(
        name=name,
        time_to_prepare=time_to_prepare,
        category=category,
        picture=picture,
        summary=summary,
        calories=calories,
        carbo=carbo,
        fats=fats,
        proteins=proteins,
        cholesterol=cholesterol,
        created_by=created_by
    )

    with db.connection.get_session() as session:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    return recipe


def get_all_recipes():
    """Get all recipes"""

    with db.connection.get_session() as session:
        return (
            session.query(Recipe)
            .join(Recipe.category, isouter=True)
            .filter(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        )


def get_recipe_by_id(recipe_id: int):
    """Get recipe by id"""

    with db.connection.get_session() as session:

        recipe = (session.query(Recipe)
                  .join(Recipe.category, isouter=True)
                  .where(Recipe.id==recipe_id)
                  .filter(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
                  .first())
        if not recipe:
            raise RecipeNotFoundException
        return recipe

def update_recipe(recipe_id: int, field: str, value: str, updated_by: str):
    """Update recipe"""

    with db.connection.get_session() as session:
        db_recipe = session.query(Recipe).where(Recipe.id == recipe_id).first()

        if not db_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        try:
            # Build the update statement
            stmt = update(Recipe).where(Recipe.id == recipe_id).values({field: value, 'updated_by': updated_by})
            session.execute(stmt)

            # Update the corresponding attribute in the SQLAlchemy model
            setattr(db_recipe, field, value)

            # Commit the changes and refresh the model
            session.commit()
            session.refresh(db_recipe)

            return db_recipe

        except sqlalchemy.exc.IntegrityError as exc:
            raise RecipeNotFoundException(exc)


def delete_recipe(*, recipe_id: int, deleted_by: int):
    recipe = get_recipe_by_id(recipe_id)

    with db.connection.get_session() as session:
        session.execute(
            update(Recipe), [{
                    "id": recipe.id,
                    "is_deleted": True,
                    "deleted_on": datetime.utcnow(),
                    "deleted_by": deleted_by
                }]
        )
        session.commit()
        return recipe


