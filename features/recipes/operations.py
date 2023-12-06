"""Recipes feature business logic"""
import math
from datetime import datetime
from typing import Type

import sqlalchemy.exc
from sqlalchemy import update, and_, desc, asc, or_

import db.connection
from .exceptions import CategoryNotFoundException, CategoryNameViolationException, RecipeNotFoundException, \
    InstructionNotFoundException, InstructionNameViolationException, RecipeWithInstructionNotFoundException
from .input_models import CreateInstructionInputModel
from .models import RecipeCategory, Recipe, RecipeInstruction
from .responses import InstructionResponse, PageResponse, RecipeResponse


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
            create_instructions(instructions, recipe)
            session.refresh(recipe)
    return recipe


def sort_recipes(sorting: str) -> list:
    """
    Create order expression
    :param sorting:
    :return:
    """
    order_expression = []

    if sorting:
        for data in sorting.split(','):
            data = data.split(':')
            sort_column = data[0]
            direction = data[1] if len(data) > 1 else None

            column = getattr(Recipe, sort_column, None)

            if column is None:
                if sort_column == 'category.name':
                    column = getattr(RecipeCategory, 'name', None)
                elif sort_column == 'category.id':
                    column = getattr(RecipeCategory, 'id', None)

            ordering = desc(column) if direction == 'desc' else asc(column)
            order_expression.append(ordering)
    else:
        order_expression.append(desc(Recipe.id))
    return order_expression


def fiter_recipes(filters: str) -> list:
    """
    Create filter expression
    :param filters:
    :return:
    """
    filter_expression = []

    if filters:
        filters = filters.split(',')

        for data in filters:
            data = data.split(':')
            filter_name = data[0]
            conditions = data[1]

            if filter_name == 'category':
                conditions = conditions.split('*')
                filter_expression.append(or_(RecipeCategory.name.ilike(x) for x in conditions))
            elif filter_name == 'complexity':
                start, end = conditions.split('-')
                filter_expression.append(Recipe.complexity.between(int(start), int(end)))
            elif filter_name == 'time_to_prepare':
                start, end = conditions.split('-')
                filter_expression.append(Recipe.time_to_prepare.between(int(start), int(end)))
            elif filter_name == 'created_by':
                creator_id = int(conditions)
                filter_expression.append(Recipe.created_by == creator_id)

    return filter_expression


def get_all_recipes(paginated_input_model) -> PageResponse:
    """
    Get all recipes paginated, sortd, and filtered
    :param paginated_input_model:
    :return:
    """
    current_page = paginated_input_model.page
    page_size = paginated_input_model.page_size

    order_expression = sort_recipes(paginated_input_model.sorting)
    filter_expression = fiter_recipes(paginated_input_model.filters)

    with db.connection.get_session() as session:
        filtered_recipes = session.query(Recipe) \
            .join(RecipeCategory) \
            .filter(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)), *filter_expression) \
            .order_by(*order_expression)

        total_items = filtered_recipes.count()
        total_pages = math.ceil(total_items / page_size)

        current_page = total_pages if current_page > total_pages else current_page

        if total_items > 0:
            limit = page_size
            offset = (current_page - 1) * limit

            filtered_recipes = filtered_recipes.offset(offset).limit(limit)

        sorting = f'&sorting={paginated_input_model.sorting}' if paginated_input_model.sorting else ''
        filters = f'&filters={paginated_input_model.filters}' if paginated_input_model.filters else ''

        response = PageResponse(
            page_number=current_page,
            page_size=page_size,
            previous_page=f"recipes/?page={current_page - 1}&page_size={page_size}{sorting}{filters}" if current_page - 1 > 0 else None,
            next_page=f"recipes/?page={current_page + 1}&page_size={page_size}{sorting}{filters}" if current_page < total_pages else None,
            total_pages=total_pages,
            total_items=total_items,
            recipes=[RecipeResponse(**r.__dict__) for r in filtered_recipes],
        )
        return response


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

        recipe.complexity = round(total_complexity / complexity_len, 1)
        recipe.time_to_prepare = time_to_prepare

        session.add(recipe)
        session.commit()
        session.refresh(recipe)


def create_instructions(instructions_request: list[CreateInstructionInputModel], recipe: Recipe) -> None:
    """
    Create instructions

    :param instructions_request:
    :param recipe:
    :return:
    """

    with db.connection.get_session() as session:
        for instruction in instructions_request:
            new_instruction = RecipeInstruction(**instruction.model_dump())
            new_instruction.recipe_id = recipe.id
            session.add(new_instruction)
            session.commit()

    update_recipe(recipe_id=recipe.id)


def get_instruction_by_id(instruction_id: int):
    """Get instruction by id"""

    with db.connection.get_session() as session:
        instruction = session.query(RecipeInstruction).filter(RecipeInstruction.id == instruction_id).first()
        if not instruction:
            raise InstructionNotFoundException
        return instruction


def update_instruction(recipe_id: int, instruction_id, field: str, value: str):
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

            update_recipe(recipe_id=recipe_id)

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

        update_recipe(recipe_id=recipe_id)
    return instruction


def delete_instruction(recipe_id: int, instruction_id):
    recipe = get_recipe_by_id(recipe_id)
    instruction = get_instruction_by_id(instruction_id)

    if instruction.recipe_id != recipe_id:
        raise RecipeWithInstructionNotFoundException

    with db.connection.get_session() as session:
        session.delete(instruction)
        session.commit()

        update_recipe(recipe_id=recipe_id)


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
