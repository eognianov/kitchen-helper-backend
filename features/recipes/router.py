"""Recipes feature endpoints"""

import fastapi
import features.recipes.operations
import features.recipes.responses
import features.recipes.exceptions

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