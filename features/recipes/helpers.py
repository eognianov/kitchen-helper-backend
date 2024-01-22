import math
from datetime import datetime, timedelta

from fastapi import Query
from sqlalchemy import desc, asc, func, or_, distinct

import db.connection
from features.recipes.input_models import PSFRecipesInputModel
from features.recipes.models import RecipeCategory, Recipe, RecipeIngredient
from features.recipes.responses import RecipeResponse, PSFRecipesResponseModel


def paginate_recipes(filtered_recipes: Query, paginated_input_model: PSFRecipesInputModel) -> PSFRecipesResponseModel:
    """
    Create recipes paginated response
    :param filtered_recipes:
    :param paginated_input_model:
    :return:
    """
    current_page = paginated_input_model.page
    page_size = paginated_input_model.page_size

    total_items = filtered_recipes.count()
    total_pages = math.ceil(total_items / page_size)

    current_page = total_pages if current_page > total_pages else current_page

    if total_items > 0:
        offset = (current_page - 1) * page_size

        filtered_recipes = filtered_recipes.offset(offset).limit(page_size)

    sort = f'&sort={paginated_input_model.sort}' if paginated_input_model.sort else ''
    filters = f'&filters={paginated_input_model.filters}' if paginated_input_model.filters else ''
    previous_page = (
        f"recipes/?page={current_page - 1}&page_size={page_size}{sort}{filters}" if current_page - 1 > 0 else None
    )
    next_page = (
        f"recipes/?page={current_page + 1}&page_size={page_size}{sort}{filters}" if current_page < total_pages else None
    )

    response = PSFRecipesResponseModel(
        page_number=current_page,
        page_size=page_size,
        previous_page=previous_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
        recipes=[RecipeResponse(**r.to_dict()) for r in filtered_recipes],
    )
    return response


def filter_recipes(filters: str) -> list:
    """
    Create filter expression
    :param filters:
    :return:
    """
    filter_expression = []

    filter_fields = (
        'category',
        'created_by',
        'period',
        'ingredient',
        'search',
        'ingredient',
        'published',
        'deleted'
    )

    # different filters are separated with commas ","
    # example: &filters=complexity:0-3,time_to_prepare:0-20,created_by:1,period:3,category:1-2
    # filters recipes with complexity less than or equal to 3, time to prepare less than or equal to 20, created by
    # user with id = 1 in the last 3 days and belonging to categories with ids 1 or 2.

    for data in filters.split(','):
        data = data.split(':')
        filter_name = data[0]
        conditions = data[1] if len(data) > 1 else None

        if filter_name not in filter_fields:
            raise ValueError(f"Invalid filter: {filter_name}")

        if not conditions:
            raise ValueError(f"Invalid conditions for {filter_name}")

        # &filters=complexity:1-5 / from(number)-to(number) separated with "-" / using range to avoid lt, gt ...
        if filter_name == 'complexity':
            conditions = conditions.split('-')
            try:
                filter_expression.append(Recipe.complexity.between(float(conditions[0]), float(conditions[1])))
            except (ValueError, IndexError):
                raise ValueError(f"Invalid range for {filter_name}.")

        # &filters=time_to_prepare:0-20 / from(number)-to(number) separated with "-" / using range to avoid lt, gt ...
        if filter_name == 'time_to_prepare':
            conditions = conditions.split('-')
            try:
                filter_expression.append(Recipe.time_to_prepare.between(int(conditions[0]), int(conditions[1])))
            except (ValueError, IndexError):
                raise ValueError(f"Invalid range for {filter_name}.")

        # &filters=created_by:1 /filter by creator id
        if filter_name == 'created_by':
            try:
                filter_expression.append(Recipe.created_by == int(conditions))
            except ValueError:
                raise ValueError(f"Invalid input for {filter_name}, must be integer.")

        # &filters=period:3 / filter all recipes from last (number) days
        if filter_name == 'period':
            try:
                days = int(conditions)
                if days < 1:
                    raise ValueError
                period = datetime.now() - timedelta(days=days)
                filter_expression.append(Recipe.created_on >= period)
            except ValueError:
                raise ValueError(f"Invalid range period. Must be integer, greater then 0.")

        # &filters=category:1-2 / filter by multiple categories using ids, separated with "-"
        if filter_name == 'category':
            conditions = conditions.split('-')
            ids = []
            for category_id in conditions:
                try:
                    ids.append(int(category_id))
                except ValueError:
                    raise ValueError(f"Category id must be an integer")
            filter_expression.append(RecipeCategory.id.in_(ids))

        # &filters=ingredient:any/all-1-2 / filter by multiple ingredient using ids, separated with "-",
        # having any of listed ingredients or having all of listed ingredients
        if filter_name == 'ingredient':
            conditions = conditions.split('-')
            ids = []

            if len(conditions) > 0 and (conditions[0].lower() == 'all' or conditions[0].lower() == 'any'):
                filter_type = conditions.pop(0)
                for ingredient_id in conditions:
                    try:
                        ids.append(int(ingredient_id))
                    except ValueError:
                        raise ValueError(f"Ingredient id must be an integer")
            else:
                raise ValueError("Invalid conditions for ingredient")

            if filter_type == 'any':
                with db.connection.get_session() as session:
                    subquery = (
                        session.query(RecipeIngredient.recipe_id)
                        .filter(RecipeIngredient.ingredient_id.in_(ids))
                        .group_by(RecipeIngredient.recipe_id)
                    )
            else:
                with db.connection.get_session() as session:
                    subquery = (
                        session.query(RecipeIngredient.recipe_id)
                        .filter(RecipeIngredient.ingredient_id.in_(ids))
                        .group_by(RecipeIngredient.recipe_id)
                        .having(func.count(distinct(RecipeIngredient.ingredient_id)) == len(ids))
                    )
            filter_expression.append(Recipe.id.in_(subquery))

        # &filters=title/summary/any:expression
        # search by word or expression in recipe name/summary/both
        if filter_name == 'search':
            conditions = conditions.split('-')

            if len(conditions) > 1 and conditions[0] in ('title', 'summary', 'any'):
                search_type = conditions.pop(0)
            else:
                raise ValueError('Invalid conditions for search')

            if search_type == 'title':
                filter_expression.append(Recipe.name.ilike(f"%{conditions[0]}%"))
            elif search_type == 'summary':
                filter_expression.append(Recipe.summary.ilike(f"%{conditions[0]}%"))
            elif search_type == 'any':
                filter_expression.append(
                    or_(Recipe.name.ilike(f"%{conditions[0]}%"), Recipe.summary.ilike(f"%{conditions[0]}%"))
                )

        # &filters=published:true/false
        if filter_name == 'published':
            if conditions not in ('true', 'false'):
                raise ValueError(f"Invalid parameter for filter published")
            else:
                condition = True if conditions == 'true' else False
            filter_expression.append(Recipe.is_published == condition)

        # &filters=deleted:true/false
        if filter_name == 'deleted':
            if conditions not in ('true', 'false'):
                raise ValueError(f"Invalid parameter for filter deleted")
            else:
                condition = True if conditions == 'true' else False
            filter_expression.append(Recipe.is_deleted == condition)

    return filter_expression


def sort_recipes(sort: str) -> list:
    """
    Create order expression
    :param sort:
    :return:
    """
    order_expression = []

    sort_fields = (
        'id',
        'name',
        'created_by',
        'created_on',
        'updated_on',
        'category.name',
        'category.id',
    )

    # default sorting
    if not sort:
        return [desc(Recipe.created_on)]

    # different sorters are separated with commas ",", directions are separated with ":"
    # example &sort=complexity:asc,created_on:desc,category.name:desc
    for data in sort.split(','):
        data = data.split(':')
        column = data[0]
        direction = data[1] if len(data) > 1 else None

        if column not in sort_fields:
            raise ValueError(f"Invalid sorting column: {column}.")

        if direction and direction not in ['asc', 'desc']:
            raise ValueError(f"Invalid sorting direction: {direction}.")

        sort_column = getattr(Recipe, column, None)

        if not sort_column:
            sort_column = getattr(RecipeCategory, column.split('.')[1], None)

        if sort_column in ['name', 'category.name']:
            ordering = desc(func.lower(sort_column)) if direction == 'desc' else asc(func.lower(sort_column))
        else:
            ordering = desc(sort_column) if direction == 'desc' else asc(sort_column)

        order_expression.append(ordering)

    return order_expression
