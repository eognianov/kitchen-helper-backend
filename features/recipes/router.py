"""Recipes feature endpoints"""

import fastapi
import features.recipes.operations
import features.recipes.responses
import features.recipes.exceptions
from .input_models import UpdateCategoryInputModel

category_router = fastapi.APIRouter()


@category_router.get('/')
def get_all_categories():
    """
    Get all categories
    :return:
    """

    categories = features.recipes.operations.get_all_recipe_categories()

    return [features.recipes.responses.Category(**_.__dict__) for _ in categories]


@category_router.get('/{category_id}')
def get_category(category_id: int = fastapi.Path()):
    """
    Get category

    :param category_id:
    :return:
    """

    try:
        category = features.recipes.operations.get_category_by_id(category_id)
        return features.recipes.responses.Category(**category.__dict__)
    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with {category_id=} does not exist"
        )


@category_router.patch('/{category_id}')
def update_category(category_id: int = fastapi.Path(), update_category_input_model: UpdateCategoryInputModel = fastapi.Body()):
    """
    Update category

    :param category_id:
    :param update_category_input_model:
    :return:
    """
    try:
        updated_category = features.recipes.operations.update_category(category_id, **update_category_input_model.model_dump())
        return features.recipes.responses.Category(**updated_category.__dict__)
    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with {category_id=} does not exist"
        )