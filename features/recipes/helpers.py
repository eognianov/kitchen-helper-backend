import math
from datetime import datetime, timedelta

import fastapi
from fastapi import Query
from sqlalchemy import desc, asc

from features.recipes.input_models import PaginateRecipiesInputModel
from features.recipes.models import RecipeCategory, Recipe
from features.recipes.responses import PageResponse, RecipeResponse


def paginate_recipes(filtered_recipes: Query, paginated_input_model: PaginateRecipiesInputModel) -> PageResponse:
    current_page = paginated_input_model.page
    page_size = paginated_input_model.page_size

    total_items = filtered_recipes.count()
    total_pages = math.ceil(total_items / page_size)

    current_page = total_pages if current_page > total_pages else current_page

    if total_items > 0:
        offset = (current_page - 1) * page_size

        filtered_recipes = filtered_recipes.offset(offset).limit(page_size)

    sorting = f'&sorting={paginated_input_model.sorting}' if paginated_input_model.sorting else ''
    filters = f'&filters={paginated_input_model.filters}' if paginated_input_model.filters else ''
    previous_page = f"recipes/?page={current_page - 1}&size={page_size}{sorting}{filters}" if current_page - 1 > 0 else None
    next_page = f"recipes/?page={current_page + 1}&page_size={page_size}{sorting}{filters}" if current_page < total_pages else None

    response = PageResponse(
        page_number=current_page,
        page_size=page_size,
        previous_page=previous_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
        recipes=[RecipeResponse(**r.__dict__) for r in filtered_recipes],
    )
    return response


def filter_recipes(filters: str, FILTERING_FIELDS: tuple) -> list:
    """
    Create filter expression
    :param filters:
    :param FILTERING_FIELDS:
    :return:
    """
    filter_expression = []

    for data in filters.split(','):

        filter_name = data.split(':')[0]
        conditions = data.split(':')[1] if len(data.split(':')) > 1 else None

        if filter_name not in FILTERING_FIELDS:
            raise fastapi.HTTPException(status_code=422, detail=f"Invalid filter: {filter_name}")

        if not conditions:
            raise fastapi.HTTPException(status_code=422, detail=f"Invalid conditions for {filter_name}")

        if filter_name == 'complexity':
            conditions = conditions.split('-')
            try:
                int(conditions[0])
                int(conditions[1])
                filter_expression.append(Recipe.complexity.between(int(conditions[0]), int(conditions[1])))
            except (ValueError, IndexError):
                raise fastapi.HTTPException(status_code=422, detail=f"Invalid range for {filter_name}")

        if filter_name == 'time_to_prepare':
            conditions = conditions.split('-')
            try:
                filter_expression.append(
                    Recipe.time_to_prepare.between(int(conditions[0]), int(conditions[1])))
            except (ValueError, IndexError):
                raise fastapi.HTTPException(status_code=422, detail=f"Invalid range for {filter_name}")

        if filter_name == 'created_by':
            try:
                filter_expression.append(Recipe.created_by == conditions)
            except ValueError:
                raise fastapi.HTTPException(status_code=422,
                                            detail=f"Invalid input for {filter_name}, must be integer")

        if filter_name == 'period':
            try:
                days = int(conditions)
                if days < 1:
                    raise ValueError
                period = datetime.now() - timedelta(days=days)
                filter_expression.append(Recipe.created_on >= period)
            except ValueError:
                raise fastapi.HTTPException(status_code=422, detail=f"Invalid range period")

        if filter_name == 'category':
            conditions = conditions.split('-')
            ids = []
            for category_id in conditions:
                try:
                    ids.append(int(category_id))
                except ValueError:
                    raise fastapi.HTTPException(status_code=422, detail=f"Category id must be an integer")
            filter_expression.append(RecipeCategory.id.in_(ids))

    return filter_expression


def sort_recipes(sorting: str, SORTING_FIELDS: tuple) -> list:
    order_expression = []

    if not sorting:
        return [desc(Recipe.created_on)]

    for data in sorting.split(','):
        data = data.split(':')
        column = data[0]
        direction = data[1] if len(data) > 1 else None

        if column not in SORTING_FIELDS:
            raise fastapi.HTTPException(status_code=422, detail=f"Invalid sorting column: {column}")

        if direction and direction not in ['asc', 'desc']:
            raise fastapi.HTTPException(status_code=422, detail=f"Invalid sorting direction: {direction}")

        sort_column = getattr(Recipe, column, None)
        if not sort_column:
            sort_column = getattr(RecipeCategory, column.split('.')[1], None)

        ordering = desc(sort_column) if direction == 'desc' else asc(sort_column)
        order_expression.append(ordering)

    return order_expression
