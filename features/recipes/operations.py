"""Recipes feature business logic"""
from datetime import datetime
from typing import Type, Optional

import sqlalchemy.exc
from sqlalchemy import update, and_, or_

import common.authentication
import db.connection
from .exceptions import (
    CategoryNotFoundException,
    CategoryNameViolationException,
    RecipeNotFoundException,
    InstructionNotFoundException,
    InstructionNameViolationException,
    RecipeWithInstructionNotFoundException,
    IngredientDoesNotExistException,
)
from .helpers import paginate_recipes
from .input_models import CreateInstructionInputModel, PSFRecipesInputModel, IngredientInput
from .models import (
    RecipeCategory,
    Recipe,
    RecipeInstruction,
    Ingredient,
)

from .input_models import PatchRecipeInputModel
from .responses import InstructionResponse, PSFRecipesResponseModel

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
    created_by: common.authentication.AuthenticatedUser,
    category_id: int = None,
    picture: str = None,
    summary: str = None,
    calories: float = 0,
    carbo: float = 0,
    fats: float = 0,
    proteins: float = 0,
    cholesterol: float = 0,
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
        created_by=created_by.id,
    )

    with db.connection.get_session() as session:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        if instructions:
            create_instructions(instructions, recipe.id, created_by)
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
    """Get recipe by id"""

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


def update_recipe(recipe_id: int, created_by: common.authentication.AuthenticatedUser) -> None:
    """
    Update recipe after adding or editing instructions
    :param created_by:
    :param recipe_id:
    :return:
    """

    with db.connection.get_session() as session:
        recipe = get_recipe_by_id(recipe_id=recipe_id, user=created_by)

        total_complexity = sum([InstructionResponse(**x.__dict__).complexity for x in recipe.instructions])
        complexity_len = len([InstructionResponse(**x.__dict__).complexity for x in recipe.instructions])
        time_to_prepare = sum([InstructionResponse(**x.__dict__).time for x in recipe.instructions])

        if complexity_len == 0:
            recipe.complexity = 0
        else:
            recipe.complexity = round(total_complexity / complexity_len, 1)

        recipe.time_to_prepare = time_to_prepare

        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    logging.info(f"Recipe #{recipe_id} was updated")


def create_instructions(
    instructions_request: list[CreateInstructionInputModel],
    recipe_id: int,
    created_by: common.authentication.AuthenticatedUser,
) -> None:
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
    update_recipe(recipe_id=recipe_id, created_by=created_by)


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

            update_recipe(recipe_id=recipe.id, created_by=user)
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

        update_recipe(recipe_id=recipe.id, created_by=user)
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
        update_recipe(recipe_id=recipe.id, created_by=user)


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


def get_ingredient_from_db(*, pk: int = None, name: str = None):
    """
    Get ingredient from database

    :param pk:
    :param name:
    :return:
    """
    with db.connection.get_session() as session:
        query = session.query(Ingredient)
        filters = []

        if pk:
            filters.append(Ingredient.id == pk)
        elif name:
            filters.append(Ingredient.name == name)

        if filters:
            query = query.filter(*filters, Ingredient.is_deleted == False)

        ingredient = query.first()
        if not ingredient:
            raise IngredientDoesNotExistException()

    return ingredient


def get_all_ingredients_from_db():
    """
    Get all ingredients from database
    :return:
    """
    with db.connection.get_session() as session:
        all_ingredients = session.query(Ingredient).filter(Ingredient.is_deleted == False).all()
        session.close()
    return all_ingredients


def create_or_get_ingredient(ingredient: IngredientInput, created_by: int):
    """
    Create a new ingredient or get an existing one by name
    :param ingredient:
    :param created_by:
    :return:
    """
    try:
        ingredient = get_ingredient_from_db(name=ingredient.name.lower())
        return ingredient
    except IngredientDoesNotExistException:
        new_ingredient = Ingredient(
            name=ingredient.name.lower(),
            calories=ingredient.calories,
            carbo=ingredient.carbo,
            fats=ingredient.fats,
            protein=ingredient.protein,
            cholesterol=ingredient.cholesterol,
            measurement=ingredient.measurement.lower(),
            category=ingredient.category.lower(),
            created_by=created_by,
        )

        with db.connection.get_session() as session:
            session.add(new_ingredient)
            session.commit()
            session.refresh(new_ingredient)

        return new_ingredient


def delete_ingredient(pk: int, user_id: int):
    """
    Delete ingredient
    :param pk:
    :param user_id:
    :return:
    """
    ingredient = get_ingredient_from_db(pk=pk)
    if not ingredient:
        raise IngredientDoesNotExistException()
    with db.connection.get_session() as session:
        ingredient.is_deleted = True
        ingredient.deleted_by = user_id
        ingredient.deleted_on = datetime.utcnow()
        session.add(ingredient)
        session.commit()
        session.refresh(ingredient)
        session.close()


def update_ingredient(ingredient_id: int, field: str, value: str | float, updated_by: int):
    """
    Update Ingredient

    :param ingredient_id:
    :param field:
    :param value:
    :param updated_by:
    :return:
    """

    db_ingredient = get_ingredient_from_db(pk=ingredient_id)
    with db.connection.get_session() as session:
        session.execute(
            update(Ingredient),
            [{"id": ingredient_id, f"{field}": str(value), "updated_by": updated_by}],
        )
        session.commit()
        session.add(db_ingredient)
        session.refresh(db_ingredient)

        logging.info(f"Ingredient #{db_ingredient.id} updated. {updated_by} set {field}={value}")
        return db_ingredient


def patch_recipe(
    *, recipe_id: int, patch_input_model: PatchRecipeInputModel, patched_by: common.authentication.AuthenticatedUser
):
    """
    Patch recipe

    :param recipe_id:
    :param patch_input_model:
    :param patched_by:
    :return:
    """

    recipe = get_recipe_by_id(recipe_id, patched_by)
    with db.connection.get_session() as session:
        values = {patch_input_model.field: patch_input_model.value, 'updated_by': patched_by.id}
        if patch_input_model.field.upper() == 'IS_PUBLISHED':
            values['published_on'] = datetime.utcnow()
            values['published_by'] = patched_by.id
        session.execute(update(Recipe).where(Recipe.id == recipe.id).values(values))
        session.commit()
        session.add(recipe)
        session.refresh(recipe)

    return recipe
