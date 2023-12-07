import math
from datetime import datetime, timedelta

from fastapi import Query
from sqlalchemy import or_, desc, asc

from features.recipes.models import RecipeCategory, Recipe
from features.recipes.input_models import PaginateRecipiesInputModel
from features.recipes.responses import PageResponse, RecipeResponse


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
            elif filter_name == 'period':
                number, condition = conditions.split('-')
                period = datetime.now() - timedelta(days=int(number))
                filter_expression.append(Recipe.created_on >= period)

    return filter_expression


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


def paginate_recipes(filtered_recipes: Query, paginated_input_model: PaginateRecipiesInputModel) -> PageResponse:
    current_page = paginated_input_model.page
    page_size = paginated_input_model.size

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
