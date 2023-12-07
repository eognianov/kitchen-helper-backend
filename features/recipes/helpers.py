import math
from datetime import datetime, timedelta

from fastapi import Query
from sqlalchemy import or_, desc, asc

from features.recipes.input_models import PaginateRecipiesInputModel
from features.recipes.models import RecipeCategory, Recipe
from features.recipes.responses import PageResponse, RecipeResponse


def filter_recipes(filters: dict) -> list:
    """
    Create filter expression
    :param filters:
    :return:
    """
    filter_expression = []

    if not filters:
        return filter_expression

    for filter_name, conditions in filters.items():
        if filter_name == 'category':
            filter_expression.append(RecipeCategory.id.in_(conditions))
        elif filter_name == 'complexity':
            start, end = conditions
            filter_expression.append(Recipe.complexity.between(start, end))
        elif filter_name == 'time_to_prepare':
            start, end = conditions
            filter_expression.append(Recipe.time_to_prepare.between(start, end))
        elif filter_name == 'created_by':
            filter_expression.append(Recipe.created_by == conditions)
        elif filter_name == 'period':
            period = datetime.now() - timedelta(days=conditions)
            filter_expression.append(Recipe.created_on >= period)

    return filter_expression


def sort_recipes(sorting: list) -> list:
    """
    Create order expression
    :param sorting:
    :return:
    """
    order_expression = []

    if not sorting:
        return [desc(Recipe.created_on)]

    for sort_column, direction in sorting:
        column = getattr(Recipe, sort_column, None)
        if column is None:
            column = getattr(RecipeCategory, sort_column.split('.')[1], None)

        ordering = desc(column) if direction == 'desc' else asc(column)
        order_expression.append(ordering)

    return order_expression


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
