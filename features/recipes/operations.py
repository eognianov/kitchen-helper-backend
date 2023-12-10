"""Recipes feature business logic"""
from typing import Type, List
import sqlalchemy.exc
from sqlalchemy import and_
import db.connection
from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError


from .exceptions import RecipesCategoryNotFoundException, RecipesCategoryNameViolationException,\
    RecipeNotFoundException, InstructionNotFoundException, InstructionNameViolationException,\
    RecipeWithInstructionNotFoundException, IngredientIntegrityViolation,\
    IngredientCategoryNotFoundException, IngredientCategoryIntegrityViolation, \
    IngredientCategoryNameViolation

from .input_models import CreateInstructionInputModel, PatchIngredientInputModel, \
    PatchIngredientCategoryInputModel,\
    CreateIngredientInputModel

from .models import RecipeCategory, Recipe,\
    RecipeInstruction, IngredientCategory, Ingredient

from .responses import InstructionResponse
from datetime import datetime

import khLogging

logging = khLogging.Logger.get_child_logger(__file__)


def get_all_ingredients_category() -> List[PatchIngredientCategoryInputModel]:

    """Get all ingredients categories
    ...
    :return: list of ingredients categories
    :rtype: List[IngredientCategory]
    """

    with db.connection.get_session() as session:
        return (
            session.query(PatchIngredientCategoryInputModel)
            .filter(PatchIngredientCategoryInputModel.is_deleted is False)
            .all()
        )


def get_ingredient_category_by_id(category_id: int) -> Type[PatchIngredientCategoryInputModel]:
    """Get ingredient category by id
    ...
    :return: ingredient category
    :rtype: IngredientCategory
    """

    with db.connection.get_session() as session:
        category = (
            session.query(IngredientCategory)
            .filter(IngredientCategory.id == category_id)
            .first()
        )

        if not category:
            raise IngredientCategoryNotFoundException()
        return category


def update_ingredient_category(
    category_id: int, field: str, value: str, updated_by: str
) -> Type[PatchIngredientCategoryInputModel]:
    """Update ingredient category
    ...
    :return: updated ingredient category
    :rtype: IngredientCategory
    """

    category = get_ingredient_category_by_id(category_id)

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(IngredientCategory)
                .where(IngredientCategory.id == category_id)
                .values({field: value, "updated_by": updated_by})
            )
            setattr(category, field, value)
            session.commit()

            return category
    except IntegrityError as ex:
        raise IngredientCategoryIntegrityViolation(ex)


def create_ingredient_category(name: str, created_by: str) -> Type[PatchIngredientCategoryInputModel]:
    """Create ingredient category
    ...
    :return: created ingredient category
    :rtype: IngredientCategory
    """

    try:
        category = IngredientCategory(name=name, created_by=created_by)
        with db.connection.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
    except IntegrityError as ex:
        raise IngredientCategoryNameViolation(ex)


def create_ingredient(ingredient: CreateIngredientInputModel):
    try:
        db_ingredient = Ingredient(**ingredient.model_dump())

        with db.connection.get_session() as session:
            session.add(db_ingredient)
            session.commit()
            session.refresh(db_ingredient)

        return db_ingredient

    except IntegrityError as ex:
        raise IngredientIntegrityViolation(ex)


def get_ingredient(ingredient_id: int) -> PatchIngredientInputModel:
    with db.connection.get_session() as session:
        ingredient = (
            session.query(Ingredient)
            .filter(Ingredient.id == ingredient_id, Ingredient.is_deleted is False)
            .first()
        )

        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

    return ingredient


def get_all_ingredients(self):
    with db.connection.get_session() as session:
        ingredients = (
            session.query(Ingredient).filter(Ingredient.is_deleted is False).all()
        )

    return ingredients


def update_ingredient(ingredient_id: int, field: str, value: str):
    with db.connection.get_session() as session:
        db_ingredient = (
            session.query(Ingredient)
            .filter(Ingredient.id == ingredient_id, Ingredient.is_deleted is False)
            .first()
        )

        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        try:
            stmt = (
                update(Ingredient)
                .where(Ingredient.id == ingredient_id)
                .values({field: value})
            )
            session.execute(stmt)

            setattr(db_ingredient, field, value)

            session.commit()

            return db_ingredient

        except IntegrityError as exc:
            raise IngredientIntegrityViolation(exc)


def delete_ingredient(ingredient_id: int) -> PatchIngredientInputModel:

    db_ingredient = get_ingredient(ingredient_id)

    if db_ingredient.is_deleted:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(Ingredient)
                .where(Ingredient.id == ingredient_id)
                .values({"is_deleted": True})
            )
            db_ingredient.is_deleted = True

            session.commit()
            session.refresh(db_ingredient)

            return {"message": "Ingredient soft-deleted"}

    except IntegrityError as ex:
        raise IngredientIntegrityViolation(ex)


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
            raise RecipesCategoryNotFoundException()
        return category


def update_category(category_id: int, field: str, value: str, updated_by: str = 'me') -> Type[RecipeCategory]:
    """Update category"""
    category = get_category_by_id(category_id)
    try:
        with db.connection.get_session() as session:
            session.execute(update(RecipeCategory), [{"id": category.id, f"{field}": value, "updated_by": updated_by}])
            session.commit()
            RecipeCategory.__setattr__(category, field, value)
            logging.info(f"User {updated_by} updated Category (#{category_id}). Set {field} to {value}")
            return category
    except sqlalchemy.exc.IntegrityError as ex:
        raise RecipesCategoryNameViolationException(ex)


def create_category(category_name: str, created_by: int = 1) -> RecipeCategory:
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
        raise RecipesCategoryNameViolationException(ex)


def create_recipe(*, name: str, time_to_prepare: int, category_id: int = None, picture: str = None, summary: str = None,
                  calories: float = 0, carbo: float = 0, fats: float = 0, proteins: float = 0, cholesterol: float = 0,
                  created_by: int = 1, instructions: list[CreateInstructionInputModel]):
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
            session.query(Recipe)
            .join(Recipe.category, isouter=True)
            .filter(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        )


def get_recipe_by_id(recipe_id: int):
    """Get recipe by id"""

    with db.connection.get_session() as session:
        recipe = (session.query(Recipe)
                  .join(Recipe.category, isouter=True)
                  .where(Recipe.id == recipe_id)
                  .filter(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
                  .first())
        if not recipe:
            raise RecipeNotFoundException
        return recipe


def update_recipe(recipe_id: int) -> None:
    """
    Update recipe after adding or editing instructions

    :param recipe_id:
    :return:
    """

    with db.connection.get_session() as session:
        recipe = get_recipe_by_id(recipe_id=recipe_id)

        total_complexity = (sum([InstructionResponse(**x.__dict__).complexity for x in recipe.instructions]))
        complexity_len = (len([InstructionResponse(**x.__dict__).complexity for x in recipe.instructions]))
        time_to_prepare = (sum([InstructionResponse(**x.__dict__).time for x in recipe.instructions]))

        if complexity_len == 0:
            recipe.complexity = 0
        else:
            recipe.complexity = round(total_complexity / complexity_len, 1)

        recipe.time_to_prepare = time_to_prepare

        session.add(recipe)
        session.commit()
        session.refresh(recipe)
    logging.info(f"Recipe #{recipe_id} was updated")


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


def create_instruction(recipe_id: int, instruction_request):
    """
    Create instructions
    :param recipe_id:
    :param instruction_request:
    """

    recipe = get_recipe_by_id(recipe_id)
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


def delete_instruction(recipe_id: int, instruction_id: int):
    recipe = get_recipe_by_id(recipe_id)
    instruction = get_instruction_by_id(instruction_id)

    if instruction.recipe_id != recipe_id:
        raise RecipeWithInstructionNotFoundException

    with db.connection.get_session() as session:
        session.delete(instruction)
        session.commit()
        logging.info(f"Instruction #{instruction_id} was deleted from Recipe #{recipe_id}")
        update_recipe(recipe_id=recipe.id)


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
