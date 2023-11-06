"""Recipes feature endpoints"""

import fastapi
import features.recipes.operations
import features.recipes.responses

category_router = fastapi.APIRouter()


@category_router.get('/')
def get_all_categories():
    """
    Get all categories
    :return:
    """

    categories = features.recipes.operations.get_all_recipe_categories()

    return [features.recipes.responses.Category(**_.__dict__) for _ in categories]
