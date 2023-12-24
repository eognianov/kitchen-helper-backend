"""Recipes feature business logic"""
from datetime import datetime
from typing import Type, Optional

import sqlalchemy.exc
from sqlalchemy import update, and_, or_
from fastapi import Depends

from sqlalchemy.orm.exc import NoResultFound
import common.authentication
import db.connection
from .exceptions import (
    CategoryNotFoundException,
    CategoryNameViolationException,
    RecipeNotFoundException,
    InstructionNotFoundException,
    InstructionNameViolationException,
    RecipeWithInstructionNotFoundException,
    UnauthorizedAccessException,
)
from .helpers import paginate_recipes
from .input_models import CreateInstructionInputModel, PSFRecipesInputModel
from .models import RecipeCategory, Recipe, RecipeInstruction
from .responses import InstructionResponse, PSFRecipesResponseModel

from features.users.authentication import AdminOrMe

import configuration
import khLogging

CONFIG = configuration.Config()

logging = khLogging.Logger.get_child_logger(__file__)


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

    param category_id:
    :return:
    """

    with db.connection.get_session() as session:
        category = session.query(RecipeCategory).where(RecipeCategory.id == category_id).first()
        if not category:
            raise CategoryNotFoundException()
        return category


def update_category(category_id: int, field: str, value: str, updated_by: int) -> Type[RecipeCategory]:
    """Update category"""
    category = get_category_by_id(category_id)
    try:
        with db.connection.get_session() as session:
            session.execute(
                update(RecipeCategory),
                [{"id": category.id, f"{field}": value, "updated_by": updated_by}],
            )
            session.commit()
            RecipeCategory.__setattr__(category, field, value)
            logging.info(f"User {updated_by} updated Category (#{category_id}). Set {field} to {value}")
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise CategoryNameViolationException(ex)


def create_category(category_name: str, created_by: int) -> RecipeCategory:
    """Create category"""

    try:
        category = RecipeCategory(name=category_name, created_by=created_by)
        with db.connection.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            logging.info(f"User {created_by} created Category (#{category.id}).")
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise CategoryNameViolationException(ex)


def create_recipe(
    *,
    name: str,
    time_to_prepare: int,
    category_id: int = None,
    picture: str = None,
    summary: str = None,
    calories: float = 0,
    carbo: float = 0,
    fats: float = 0,
    proteins: float = 0,
    cholesterol: float = 0,
    created_by: int = 1,
    instructions: list[CreateInstructionInputModel],
):
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
    :param instructions:
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
        created_by=created_by,
    )

    with db.connection.get_session() as session:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        if instructions:
            create_instructions(instructions, recipe.id)
            session.refresh(recipe)
    logging.info(f"User {created_by} create Recipe (#{recipe.id}).")
    return recipe


def _get_published_filter_expression(user: Optional[common.authentication.AuthenticatedUser]):
    """
    Get published filters

    :param user:
    :return:
    """
    published_expression = []

    if user:
        if not user.is_admin:
            published_expression.append(and_(Recipe.is_deleted.is_(False)))
            published_expression.append(and_(or_(Recipe.created_by.is_(user.id), Recipe.is_published.is_(True))))
    else:
        published_expression = [and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True))]

    return published_expression


def get_all_recipes(
    paginated_input_model: PSFRecipesInputModel, user: common.authentication.AuthenticatedUser
) -> PSFRecipesResponseModel:
    """
    Get all recipes paginated, sorted, and filtered
    :param paginated_input_model:
    :param user:
    :return:
    """

    filter_expression = paginated_input_model.filter_expression
    order_expression = paginated_input_model.order_expression
    published_expression = _get_published_filter_expression(user)
    filter_expression.extend(published_expression)

    with db.connection.get_session() as session:
        filtered_recipes = (
            session.query(Recipe)
            .join(RecipeCategory, isouter=True)
            .filter(
                *filter_expression,
            )
            .order_by(*order_expression)
        )

        response = paginate_recipes(filtered_recipes, paginated_input_model)
        return response


def get_recipe_by_id(recipe_id: int, user: common.authentication.AuthenticatedUser = None):
    """
    Get recipe by id
    :param recipe_id:
    :param user:
    :return:
    """

    filters = _get_published_filter_expression(user)

    with db.connection.get_session() as session:
        recipe = (
            session.query(Recipe)
            .join(Recipe.category, isouter=True)
            .where(Recipe.id == recipe_id)
            .filter(and_(*filters))
            .first()
        )
        if not recipe:
            raise RecipeNotFoundException
        return recipe


def update_recipe(recipe_id: int, user: common.authentication.AuthenticatedUser):
    """
    Update recipe
    :param recipe_id:
    :param user:
    :return:
    """

    recipe = get_recipe_by_id(recipe_id)

    if user != 'admin' and user != recipe.created_by:
        raise UnauthorizedAccessException(f"User {user.id} is not authorized to update Recipe #{recipe_id}")

    with db.connection.get_session() as session:
        session.execute(
            update(Recipe),
            [
                {
                    "id": recipe.id,
                    "name": recipe.name,
                    "time_to_prepare": recipe.time_to_prepare,
                    "category_id": recipe.category_id,
                    "picture": recipe.picture,
                    "summary": recipe.summary,
                    "calories": recipe.calories,
                    "carbo": recipe.carbo,
                    "fats": recipe.fats,
                    "proteins": recipe.proteins,
                    "cholesterol": recipe.cholesterol,
                    "created_by": recipe.created_by,
                    "is_published": recipe.is_published,
                    "is_deleted": recipe.is_deleted,
                    "deleted_on": recipe.deleted_on,
                    "deleted_by": recipe.deleted_by,
                    "updated_by": recipe.updated_by,
                }
            ],
        )
        session.commit()
        logging.info(f"Recipe #{recipe_id} was updated")


def patch_recipe(recipe_id: int, field: str, value: str, user: common.authentication.AuthenticatedUser) -> Type[Recipe]:
    """
    Patch Recipe
    :param recipe_id:
    :param field:
    :param value:
    :param user:
    :return:
    """
    try:
        recipe = get_recipe_by_id(recipe_id, user=user)

        if not recipe.is_published:
            raise RecipeNotFoundException(f"Recipe #{recipe_id} not found or not published")

        if user != 'admin' and user != recipe.created_by:
            raise UnauthorizedAccessException(f"User {user} is not authorized to update Recipe #{recipe_id}")

        with db.connection.get_session() as session:
            session.execute(
                update(Recipe).where(Recipe.id == recipe.id).values({f"{field}": value, "updated_by": user})
            )
            session.commit()
            Recipe.__setattr__(recipe, field, value)
            logging.info(f"User {user} updated Recipe (#{recipe_id}). Set {field} to {value}")
            return recipe

    except NoResultFound:
        raise RecipeNotFoundException(f"Recipe #{recipe_id} not found")

    except sqlalchemy.exc.IntegrityError as ex:
        raise CategoryNameViolationException(ex)


def create_instructions(instructions_request: list[CreateInstructionInputModel], recipe_id: int) -> None:
    """
    Create instructions
    :param instructions_request:
    :param recipe_id:
    :return:
    """

    with db.connection.get_session() as session:
        for instruction in instructions_request:
            new_instruction = RecipeInstruction(**instruction.model_dump())
            new_instruction.recipe_id = recipe_id
            session.add(new_instruction)
            session.commit()
    logging.info(f"Recipe #{recipe_id} was updated with {len(instructions_request)} instructions")
    update_recipe(recipe_id=recipe_id)


def get_instruction_by_id(instruction_id: int):
    """Get instruction by id"""

    with db.connection.get_session() as session:
        instruction = session.query(RecipeInstruction).filter(RecipeInstruction.id == instruction_id).first()
        if not instruction:
            raise InstructionNotFoundException
        return instruction


def update_instruction(
    recipe_id: int, instruction_id: int, field: str, value: str, user: common.authentication.AuthenticatedUser
):
    """
    Update instruction
    :param recipe_id:
    :param instruction_id:
    :param field:
    :param value:
    """

    instruction = get_instruction_by_id(instruction_id)
    recipe = get_recipe_by_id(recipe_id, user=user)

    if instruction.recipe_id != recipe_id:
        raise RecipeWithInstructionNotFoundException

    try:
        with db.connection.get_session() as session:
            session.execute(update(RecipeInstruction), [{"id": instruction.id, f"{field}": value}])
            session.commit()
            RecipeInstruction.__setattr__(instruction, field, value)

            update_recipe(recipe_id=recipe.id)
            logging.info(f"Instruction #({instruction_id}) was updated. Set {field} = {value}")
            return instruction

    except sqlalchemy.exc.IntegrityError as ex:
        raise InstructionNameViolationException(ex)


def create_instruction(recipe_id: int, instruction_request, user: common.authentication.AuthenticatedUser):
    """
    Create instructions

    :param recipe_id:
    :param instruction_request:
    :param user:
    """

    recipe = get_recipe_by_id(recipe_id, user=user)
    instruction = RecipeInstruction(
        instruction=instruction_request.instruction,
        time=instruction_request.time,
        complexity=instruction_request.complexity,
        category=instruction_request.category,
    )

    with db.connection.get_session() as session:
        instruction.recipe_id = recipe.id
        session.add(instruction)
        session.commit()
        session.refresh(instruction)

        update_recipe(recipe_id=recipe.id)
    return instruction


def delete_instruction(recipe_id: int, instruction_id: int, user: Optional[common.authentication.AuthenticatedUser]):
    recipe = get_recipe_by_id(recipe_id, user=user)
    instruction = get_instruction_by_id(instruction_id)

    if instruction.recipe_id != recipe_id:
        raise RecipeWithInstructionNotFoundException

    with db.connection.get_session() as session:
        session.delete(instruction)
        session.commit()
        logging.info(f"Instruction #{instruction_id} was deleted from Recipe #{recipe_id}")
        update_recipe(recipe_id=recipe.id)


def delete_recipe(*, recipe_id: int, deleted_by: common.authentication.authenticated_user):
    """
    Delete recipe

    :param recipe_id:
    :param deleted_by:
    :return:
    """

    recipe = get_recipe_by_id(recipe_id, user=deleted_by)

    with db.connection.get_session() as session:
        session.execute(
            update(Recipe),
            [
                {
                    "id": recipe.id,
                    "is_deleted": True,
                    "deleted_on": datetime.utcnow(),
                    "deleted_by": deleted_by.id,
                }
            ],
        )
        session.commit()
        return recipe
