"""Recipes feature business logic"""
from typing import Type, List, Optional
import sqlalchemy.exc
from sqlalchemy import update, and_

import db.connection
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

import features
import features.recipes
# from .exceptions import RecipesCategoryNotFoundException, RecipesCategoryNameViolationException,\
#     RecipeNotFoundException, InstructionNotFoundException, InstructionNameViolationException,\
#     RecipeWithInstructionNotFoundException, IngredientIntegrityViolation,\
#     IngredientCategoryNotFoundException, IngredientCategoryIntegrityViolation, \
#     IngredientCategoryNameViolation

import features.recipes.exceptions
import features.recipes.models
import features.recipes.input_models
import features.recipes.responses

# from .input_models import CreateInstructionInputModel, PatchIngredientInputModel, \
#     PatchIngredientCategoryInputModel,\
#     CreateIngredientInputModel

# from .models import RecipeCategory, Recipe,\
#     RecipeInstruction, IngredientCategory, Ingredient

# from .responses import InstructionResponse
from datetime import datetime

import khLogging
from features import recipes

logging = khLogging.Logger.get_child_logger(__file__)


def get_all_ingredients_category() -> List[Optional[recipes.models.IngredientCategory]]:

    """Get all ingredients categories
    ...
    :return: list of ingredients categories
    :rtype: List[IngredientCategory]
    """

    with db.connection.get_session() as session:
        return (
            session.query(recipes.models.IngredientCategory)
            .filter(recipes.models.IngredientCategory.is_deleted is False)
            .all()
        )


def get_ingredient_category_by_id(category_id: int) -> Type[recipes.models.IngredientCategory]:
    """Get ingredient category by id
    ...
    :return: ingredient category
    :rtype: IngredientCategory
    """

    with db.connection.get_session() as session:
        category = (
            session.query(recipes.responses.IngredientCategory)
            .filter(recipes.responses.IngredientCategory.id == category_id)
            .first()
        )

        if not category:
            raise recipes.exceptions.IngredientCategoryNotFoundException()
        return category


def patch_ingredient_category(
    category_id: int, field: str, value: str, updated_by: str
) -> Type[recipes.input_models.PatchIngredientCategoryInputModel]:
    """Patch ingredient category
    ...
    :return: updated ingredient category
    :rtype: IngredientCategory
    """

    category = get_ingredient_category_by_id(category_id)

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(recipes.models.IngredientCategory)
                .where(recipes.models.IngredientCategory.id == category_id)
                .values({field: value, "updated_by": updated_by})
            )
            setattr(category, field, value)
            session.commit()

            return category
    except IntegrityError as ex:
        raise recipes.exceptions.IngredientCategoryIntegrityViolation(ex)


def create_ingredient_category(name: str, created_by: str) -> Type[recipes.input_models.PatchIngredientCategoryInputModel]:
    """Create ingredient category
    ...
    :return: created ingredient category
    :rtype: IngredientCategory
    """

    try:
        category = recipes.responses.IngredientCategory(name=name, created_by=created_by)
        with db.connection.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
    except IntegrityError as ex:
        raise recipes.exceptions.IngredientCategoryNameViolation(ex)


def create_ingredient(ingredient: recipes.input_models.CreateIngredientInputModel):
    try:
        db_ingredient = recipes.models.Ingredient(**ingredient.model_dump())

        with db.connection.get_session() as session:
            session.add(db_ingredient)
            session.commit()
            session.refresh(db_ingredient)

        return db_ingredient

    except IntegrityError as ex:
        raise recipes.exceptions.IngredientIntegrityViolation(ex)


def get_ingredient(ingredient_id: int) -> recipes.input_models.PatchIngredientInputModel:
    with db.connection.get_session() as session:
        ingredient = (
            session.query(recipes.models.Ingredient)
            .filter(recipes.models.Ingredient.id == ingredient_id, recipes.models.Ingredient.is_deleted is False)
            .first()
        )

        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

    return ingredient


def get_all_ingredients(self):
    with db.connection.get_session() as session:
        ingredients = (
            session.query(recipes.models.Ingredient).filter(recipes.models.Ingredient.is_deleted is False).all()
        )

    return ingredients


def update_ingredient(ingredient_id: int, field: str, value: str):
    with db.connection.get_session() as session:
        db_ingredient = (
            session.query(recipes.models.Ingredient)
            .filter(recipes.models.Ingredient.id == ingredient_id, recipes.models.Ingredient.is_deleted is False)
            .first()
        )

        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        try:
            stmt = (
                update(recipes.models.Ingredient)
                .where(recipes.models.Ingredient.id == ingredient_id)
                .values({field: value})
            )
            session.execute(stmt)

            setattr(db_ingredient, field, value)

            session.commit()

            return db_ingredient

        except IntegrityError as exc:
            raise recipes.exceptions.IngredientIntegrityViolation(exc)

def patch_ingredient(ingredient_id: int, field: str, value: str) -> recipes.input_models.PatchIngredientInputModel:

    db_ingredient = get_ingredient(ingredient_id)

    if db_ingredient.is_deleted:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(recipes.models.Ingredient)
                .where(recipes.models.Ingredient.id == ingredient_id)
                .values({field: value})
            )
            setattr(db_ingredient, field, value)
            session.commit()

            return db_ingredient

    except IntegrityError as ex:
        raise recipes.exceptions.IngredientIntegrityViolation(ex)


def delete_ingredient(ingredient_id: int) -> recipes.input_models.PatchIngredientInputModel:

    db_ingredient = get_ingredient(ingredient_id)

    if db_ingredient.is_deleted:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(recipes.models.Ingredient)
                .where(recipes.models.Ingredient.id == ingredient_id)
                .values({"is_deleted": True})
            )
            db_ingredient.is_deleted = True

            session.commit()
            session.refresh(db_ingredient)

            return {"message": "Ingredient soft-deleted"}

    except IntegrityError as ex:
        raise recipes.exceptions.IngredientIntegrityViolation(ex)


def get_all_recipe_categories() -> list[Type[recipes.models.RecipeCategory]]:
    """
    Get all recipe categories
    :return:
    """
    with db.connection.get_session() as session:
        return session.query(recipes.models.RecipeCategory).all()


def get_category_by_id(category_id: int) -> Type[recipes.models.RecipeCategory]:
    """
    Get category by id

    param category_id:
    :return:
    """

    with db.connection.get_session() as session:
        category = session.query(recipes.models.RecipeCategory).where(recipes.models.RecipeCategory.id == category_id).first()
        if not category:
            raise recipes.exceptions.RecipesCategoryNotFoundException()
        return category


def update_category(category_id: int, field: str, value: str, updated_by: str = 'me') -> Type[recipes.models.RecipeCategory]:
    """Update category"""
    category = get_category_by_id(category_id)
    try:
        with db.connection.get_session() as session:
            session.execute(update(recipes.models.RecipeCategory), [{"id": category.id, f"{field}": value, "updated_by": updated_by}])
            session.commit()
            recipes.models.RecipeCategory.__setattr__(category, field, value)
            logging.info(f"User {updated_by} updated Category (#{category_id}). Set {field} to {value}")
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise recipes.exceptions.RecipesCategoryNameViolationException(ex)


def create_category(category_name: str, created_by: int = 1) -> recipes.models.RecipeCategory:
    """Create category"""

    try:
        category = recipes.models.RecipeCategory(name=category_name, created_by=created_by)
        with db.connection.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            logging.info(f"User {created_by} created Category (#{category.id}).")
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise recipes.exceptions.RecipesCategoryNameViolationException(ex)


def create_recipe(*, name: str, time_to_prepare: int, created_by: int, category_id: int = None, picture: str = None, summary: str = None,
                  calories: float = 0, carbo: float = 0, fats: float = 0, proteins: float = 0, cholesterol: float = 0, instructions: list[recipes.input_models.CreateInstructionInputModel]):
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

    recipe = recipes.models.Recipe(
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
        is_published=True
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


def get_all_recipes():
    """Get all recipes"""

    with db.connection.get_session() as session:
        return (
            session.query(recipes.models.Recipe)
            .join(recipes.models.Recipe.category, isouter=True)
            .filter(and_(recipes.models.Recipe.is_deleted.is_(False), recipes.models.Recipe.is_published.is_(True)))
        )


def get_recipe_by_id(recipe_id: int):
    """Get recipe by id"""

    with db.connection.get_session() as session:
        recipe = (session.query(recipes.models.Recipe)
                  .join(recipes.models.Recipe.category, isouter=True)
                  .where(recipes.models.Recipe.id == recipe_id)
                  .filter(and_(recipes.models.Recipe.is_deleted.is_(False), recipes.models.Recipe.is_published.is_(True)))
                  .first())
        if not recipe:
            raise recipes.exceptions.RecipeNotFoundException
        return recipe


def update_recipe(recipe_id: int) -> None:
    """
    Update recipe after adding or editing instructions

    :param recipe_id:
    :return:
    """

    with db.connection.get_session() as session:
        recipe = get_recipe_by_id(recipe_id=recipe_id)

        total_complexity = (sum([recipes.responses.InstructionResponse(**x.__dict__).complexity for x in recipe.instructions]))
        complexity_len = (len([recipes.responses.InstructionResponse(**x.__dict__).complexity for x in recipe.instructions]))
        time_to_prepare = (sum([recipes.responses.InstructionResponse(**x.__dict__).time for x in recipe.instructions]))

        if complexity_len == 0:
            recipe.complexity = 0
        else:
            recipe.complexity = round(total_complexity / complexity_len, 1)

        recipe.time_to_prepare = time_to_prepare

        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    logging.info(f"Recipe #{recipe_id} was updated")


def create_instructions(instructions_request: list[recipes.input_models.CreateInstructionInputModel], recipe_id: int) -> None:
    """
    Create instructions

    :param instructions_request:
    :param recipe_id:
    :return:
    """

    with db.connection.get_session() as session:
        for instruction in instructions_request:
            new_instruction = recipes.models.RecipeInstruction(**instruction.model_dump())
            new_instruction.recipe_id = recipe_id
            session.add(new_instruction)
            session.commit()
    logging.info(f"Recipe #{recipe_id} was updated with {len(instructions_request)} instructions")
    update_recipe(recipe_id=recipe_id)


def get_instruction_by_id(instruction_id: int):
    """Get instruction by id"""

    with db.connection.get_session() as session:
        instruction = session.query(recipes.models.RecipeInstruction).filter(recipes.models.RecipeInstruction.id == instruction_id).first()
        if not instruction:
            raise recipes.exceptions.InstructionNotFoundException
        return instruction


def update_instruction(recipe_id: int, instruction_id: int, field: str, value: str):
    """
    Update instruction
    :param recipe_id:
    :param instruction_id:
    :param field:
    :param value:
    """

    instruction = get_instruction_by_id(instruction_id)
    recipe = get_recipe_by_id(recipe_id)

    if instruction.recipe_id != recipe_id:
        raise recipes.exceptions.RecipeWithInstructionNotFoundException

    try:
        with db.connection.get_session() as session:
            session.execute(update(recipes.models.RecipeInstruction), [{"id": instruction.id, f"{field}": value}])
            session.commit()
            recipes.models.RecipeInstruction.__setattr__(instruction, field, value)

            update_recipe(recipe_id=recipe.id)
            logging.info(f"Instruction #({instruction_id}) was updated. Set {field} = {value}")
            return instruction

    except sqlalchemy.exc.IntegrityError as ex:
        raise recipes.exceptions.InstructionNameViolationException(ex)


def create_instruction(recipe_id: int, instruction_request):
    """
    Create instructions
    :param recipe_id:
    :param instruction_request:
    """

    recipe = get_recipe_by_id(recipe_id)
    instruction = recipes.models.RecipeInstruction(
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


def delete_instruction(recipe_id: int, instruction_id: int):
    recipe = get_recipe_by_id(recipe_id)
    instruction = get_instruction_by_id(instruction_id)

    if instruction.recipe_id != recipe_id:
        raise recipes.exceptions.RecipeWithInstructionNotFoundException

    with db.connection.get_session() as session:
        session.delete(instruction)
        session.commit()
        logging.info(f"Instruction #{instruction_id} was deleted from Recipe #{recipe_id}")
        update_recipe(recipe_id=recipe.id)


def delete_recipe(*, recipe_id: int, deleted_by: int):
    """
    Delete recipe

    :param recipe_id:
    :param deleted_by:
    :return:
    """

    recipe = get_recipe_by_id(recipe_id)

    with db.connection.get_session() as session:
        session.execute(
            update(recipes.models.Recipe), [{
                "id": recipe.id,
                "is_deleted": True,
                "deleted_on": datetime.utcnow(),
                "deleted_by": deleted_by
            }]
        )
        session.commit()
        return recipe
