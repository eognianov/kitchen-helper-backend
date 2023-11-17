"""Recipes feature business logic"""
import db.connection
from .input_models import InstructionInput
from .models import RecipeCategory, Recipe, RecipeInstruction
from .exceptions import CategoryNotFoundException, CategoryNameViolationException, RecipeNotFoundException, \
    InstructionNotFoundException
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

    param category_id:
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
                  created_by: str = 'me', instructions: list[InstructionInput]):
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
        created_by=created_by
    )

    with db.connection.get_session() as session:
        session.add(recipe)
        session.commit()
        session.refresh(recipe)

        if instructions:
            create_instructions(instructions, recipe)
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


def update_recipe(recipe_id: int) -> None:
    """
        Update recipe after adding instruction/s

        :param recipe_id:
        :return:
    """

    with db.connection.get_session() as session:
        recipe = session.query(Recipe).filter(Recipe.id == recipe_id).first()
        instructions = session.query(RecipeInstruction).filter(RecipeInstruction.recipe_id == recipe.id)

        total_complexity = (sum([InstructionResponse(**x.__dict__).complexity for x in instructions]))
        complexity_len = (len([InstructionResponse(**x.__dict__).complexity for x in instructions]))
        time_to_prepare = (sum([InstructionResponse(**x.__dict__).time for x in instructions]))

        recipe.complexity = round(total_complexity / complexity_len, 1)
        recipe.time_to_prepare = time_to_prepare
        session.add(recipe)
        session.commit()


def create_instructions(instructions_request: list[InstructionInput], recipe: Recipe) -> None:
    """
        Create instructions

        :param instructions_request:
        :param recipe:
        :return:
    """

    with db.connection.get_session() as session:
        instructions = instructions_request

        for instruction in instructions:
            new_instruction = RecipeInstruction(**instruction.model_dump())
            new_instruction.recipe_id = recipe.id
            session.add(new_instruction)
            session.commit()

    update_recipe(recipe_id=recipe.id)


def get_instructions_by_recipe_id(recipe_id: int) -> list[RecipeInstruction]:
    """
        Get instructions by recipe_id

        :param recipe_id:
        :return:
    """

    with db.connection.get_session() as session:
        instructions = session.query(RecipeInstruction).filter(RecipeInstruction.recipe_id == recipe_id)
        return instructions


def get_instruction_by_id(instruction_id: int, recipe_id: int) -> RecipeInstruction:
    """
        Get instruction by id:

        :param instruction_id:
        :param recipe_id:
        :return:
    """

    with db.connection.get_session() as session:
        instruction = session.query(RecipeInstruction) \
            .filter(RecipeInstruction.id == instruction_id,
                    RecipeInstruction.recipe_id == recipe_id) \
            .first()
        if not instruction:
            raise InstructionNotFoundException
        return instruction


def update_instruction(instruction_request: InstructionInput, instruction: RecipeInstruction) -> RecipeInstruction:
    """
            Update instruction

            :param instruction_request:
            :param instruction:
            :return:
    """

    with db.connection.get_session() as session:
        instruction.instruction = instruction_request.instruction
        instruction.category = instruction_request.category
        instruction.time = instruction_request.time
        instruction.complexity = instruction_request.complexity

        session.add(instruction)
        session.commit()
        session.refresh(instruction)

        update_recipe(recipe_id=instruction.recipe_id)

        return instruction
