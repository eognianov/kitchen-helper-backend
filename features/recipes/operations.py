"""Recipes feature business logic"""
import db.connection
from .models import RecipeCategory, Recipe, RecipeInstruction
from .exceptions import CategoryNotFoundException, CategoryNameViolationException, RecipeNotFoundException
from typing import Type
from sqlalchemy import update
import sqlalchemy.exc

from .responses import InstructionResponse


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
                  calories: float = 0, carbo: float = 0, fats: float = 0, proteins: float = 0, cholesterol: float = 0,
                  created_by: str = 'me'):
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
        return session.query(Recipe).join(Recipe.category, isouter=True).all()


def get_recipe_by_id(recipe_id: int):
    """Get recipe by id"""

    with db.connection.get_session() as session:
        recipe = session.query(Recipe).join(Recipe.category, isouter=True).where(Recipe.id == recipe_id).first()
        if not recipe:
            raise RecipeNotFoundException
        return recipe


def get_all_instructions() -> list[Type[RecipeInstruction]]:
    """Get instructions"""

    with db.connection.get_session() as session:
        return session.query(RecipeInstruction).all()


def create_instructions_and_update_recipe(instructions_request, recipe):
    """
        Create instruction

        :param instructions_request:
        :param recipe:
        :return:
    """

    with db.connection.get_session() as session:

        instructions = instructions_request.instructions

        old_instructions = session.query(RecipeInstruction).filter(RecipeInstruction.recipe_id == recipe.id)

        old_total_complexity = (sum([InstructionResponse(**x.__dict__).complexity for x in old_instructions]))
        old_len = (len([InstructionResponse(**x.__dict__).complexity for x in old_instructions]))
        old_time_to_prepare = (sum([InstructionResponse(**x.__dict__).time for x in old_instructions]))

        total_complexity = old_total_complexity
        total_time_to_prepare = old_time_to_prepare

        for instruction in instructions:
            new_instruction = RecipeInstruction(**instruction.model_dump())
            new_instruction.recipe_id = recipe.id
            total_time_to_prepare += new_instruction.time
            total_complexity += new_instruction.complexity
            session.add(new_instruction)
            session.commit()

        recipe.complexity = round(total_complexity / (len(instructions) + old_len), 1)
        recipe.time_to_prepare = total_time_to_prepare
        session.add(recipe)
        session.commit()
