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
    RecipeIngredientDoesNotExistException,
    IngredientAlreadyInRecipe,
)
from .helpers import paginate_recipes
from .input_models import (
    CreateInstructionInputModel,
    PSFRecipesInputModel,
    IngredientInput,
    RecipeInputModel,
    RecipeIngredientInputModel,
)
from .models import (
    RecipeCategory,
    Recipe,
    RecipeInstruction,
    Ingredient,
    RecipeIngredient,
)

from .input_models import PatchRecipeInputModel
from .responses import PSFRecipesResponseModel

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
    created_by: common.authentication.AuthenticatedUser,
    category_id: int = None,
    picture: int = None,
    summary: str = None,
    serves: int,
    instructions: list[CreateInstructionInputModel],
    ingredients: list[RecipeIngredientInputModel],
):
    """
    Create recipe

    :param name:
    :param category_id:
    :param picture:
    :param summary:
    :param serves:
    :param created_by:
    :param instructions:
    :param ingredients:
    :return:
    """

    category = None
    if category_id:
        category = get_category_by_id(category_id)

    recipe = Recipe(
        name=name,
        category=category,
        picture=picture,
        summary=summary,
        serves=serves,
        created_by=created_by.id,
    )
    if instructions:
        recipe.instructions = [RecipeInstruction(**instruction.model_dump()) for instruction in instructions]

    with db.connection.get_session() as session:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        if ingredients:
            add_ingredients_to_recipe(ingredients, recipe.id, created_by)

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
            published_expression.append(and_(or_(Recipe.created_by == user.id, Recipe.is_published.is_(True))))
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
    :param user:
    """

    instruction = get_instruction_by_id(instruction_id)
    recipe = get_recipe_by_id(recipe_id, user=user)

    if instruction.recipe_id != recipe_id:
        raise RecipeWithInstructionNotFoundException

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(RecipeInstruction), [{"id": instruction.id, f"{field}": value, "updated_by": user.id}]
            )
            session.commit()
            RecipeInstruction.__setattr__(instruction, field, value)
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
            raise IngredientDoesNotExistException(text=f"Ingredient with id {pk} does not exist")

    return ingredient


def get_all_ingredients_from_db():
    """
    Get all ingredients from database
    :return:
    """
    with db.connection.get_session() as session:
        all_ingredients = session.query(Ingredient).filter(Ingredient.is_deleted == False).all()
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


def _remove_ingredient_from_all_recipes(ingredient_id: int, user: common.authentication.authenticated_user):
    """
    Remove deleted ingredient from all recipes
    :param ingredient_id:
    :param user:
    :return:
    """
    with db.connection.get_session() as session:
        ingredient = session.query(Ingredient).get(ingredient_id)

        if ingredient:
            all_recipes_with_ingredient = (
                session.query(Recipe)
                .join(RecipeIngredient)
                .filter(
                    RecipeIngredient.ingredient_id == ingredient.id,
                )
                .all()
            )

            for recipe in all_recipes_with_ingredient:
                recipe_ingredient = (
                    session.query(RecipeIngredient)
                    .filter_by(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                    )
                    .first()
                )

                if recipe_ingredient:
                    session.delete(recipe_ingredient)

                    recipe.updated_by = user.id
                    recipe.updated_on = datetime.utcnow()

                    session.commit()

            session.commit()


def delete_ingredient(pk: int, user: common.authentication.authenticated_user):
    """
    Delete ingredient and remove the relations with recipes
    :param pk:
    :param user:
    :return:
    """
    ingredient = get_ingredient_from_db(pk=pk)
    if not ingredient:
        raise IngredientDoesNotExistException(text=f"Ingredient with id {pk} does not exist")
    with db.connection.get_session() as session:
        ingredient.is_deleted = True
        ingredient.deleted_by = user.id
        ingredient.deleted_on = datetime.utcnow()
        session.add(ingredient)
        session.commit()
        session.refresh(ingredient)

        _remove_ingredient_from_all_recipes(pk, user=user)


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


def update_recipe(
    *, recipe_id: int, update_recipe_input_model: RecipeInputModel, updated_by: common.authentication.AuthenticatedUser
):
    """
    Update recipe

    :param recipe_id:
    :param update_recipe_input_model:
    :param updated_by:
    :return:
    """

    recipe = get_recipe_by_id(recipe_id, user=updated_by)
    for field, value in iter(update_recipe_input_model):
        if field.casefold() in ['instructions']:
            value = [RecipeInstruction(**instruction.model_dump()) for instruction in value]
        Recipe.__setattr__(recipe, field, value)

    recipe.updated_by = updated_by.id

    with db.connection.get_session() as session:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    return recipe


def add_ingredient_to_recipe(
    recipe_id: int, ingredient_id: int, quantity: float, user: common.authentication.AuthenticatedUser
):
    """
    Add ingredient to recipe
    :param recipe_id:
    :param ingredient_id:
    :param quantity:
    :param user:
    :return:
    """
    with db.connection.get_session() as session:
        db_ingredient = get_ingredient_from_db(pk=ingredient_id)
        db_recipe = get_recipe_by_id(recipe_id=recipe_id, user=user)

        if db_ingredient in db_recipe.ingredients:
            raise IngredientAlreadyInRecipe()

        recipe_ingredient = RecipeIngredient(recipe_id=recipe_id, ingredient_id=db_ingredient.id, quantity=quantity)

        db_recipe.updated_by = user.id
        db_recipe.updated_on = datetime.utcnow()

        session.add(recipe_ingredient)
        session.commit()
        session.add(db_recipe)
        session.commit()


def add_ingredients_to_recipe(
    ingredients: list[RecipeIngredientInputModel], recipe_id: int, user: common.authentication.authenticated_user
):
    """
    Add ingredients to recipe
    :param ingredients:
    :param recipe_id:
    :param user:
    :return:
    """
    for ingredient in ingredients:
        add_ingredient_to_recipe(recipe_id, ingredient.ingredient_id, ingredient.quantity, user=user)


def remove_ingredient_from_recipe(
    recipe: Recipe, ingredient: Ingredient, user: common.authentication.authenticated_user
):
    """
    Remove ingredient from recipe
    :param recipe:
    :param ingredient:
    :param user:
    :return:
    """
    with db.connection.get_session() as session:
        recipe_ingredient = (
            session.query(RecipeIngredient).filter_by(recipe_id=recipe.id, ingredient_id=ingredient.id).first()
        )

        if recipe_ingredient:
            session.delete(recipe_ingredient)

            recipe.updated_by = user.id
            recipe.updated_on = datetime.utcnow()

            session.commit()
        else:
            raise RecipeIngredientDoesNotExistException()
