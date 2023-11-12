"""Ingredients feature endpoints"""
from typing import List

import fastapi
import features.ingredients_api.operations
from features.ingredients_api.responses import Ingredient
import features.ingredients_api.exceptions
from .input_models import PatchIngredientInputModel, CreateIngredientInputModel

ingredients_router = fastapi.APIRouter()

@ingredients_router.get('/', response_model=List[Ingredient])
def get_all_ingredients_endpoint():
    """Get all ingredients
    ...
    :return: list of ingredients
    :rtype: List[Ingredient]
    """

    return features.ingredients_api.operations.get_all_ingredients()

@ingredients_router.get('/{ingredient_id}', response_model=Ingredient)
def get_ingredient(ingredient_id: int = fastapi.Path()):

    """Get ingredient

    :param ingredient_id: Identifier for ingredient
    :type int
    ...
    :raises HTTPException: Raised if ingredient with ingredient_id not found
    ...
    :return: Found ingredient
    :rtype: Ingredient
    """

    try:
        return features.ingredients_api.operations.get_ingredient(ingredient_id)
    except features.ingredients_api.exceptions.IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with {ingredient_id=} not found"
        )

@ingredients_router.post('/', response_model=Ingredient)
def create_ingredient(create_ingredient_input_model: CreateIngredientInputModel):

    """Create ingredient

        :param : name of ingredient
        :type str
        ...
        :param : category of ingredient
        :type str
        ...
        :param : calories of ingredient
        :type float
        ...
        :param : carbo of ingredient
        :type float
        ...
        :param : fats of ingredient
        :type float
        ...
        :param : protein of ingredient
        :type float
        ...
        :param : cholesterol of ingredient
        :type float
        ...
        :param : measurement of ingredient
        :type float
        ...
        ...
        :raises HTTPException: Raised if ingredient with the same name already exists
        ...
        :return: Created ingredient
        :rtype: Ingredient
        """

    try:
        return features.ingredients_api.operations.create_ingredient(create_ingredient_input_model.name)

    except features.ingredients_api.exceptions.IngredientNameViolationException:

        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with name {create_ingredient_input_model.name} already exists"
        )

@ingredients_router.patch('/{ingredient_id', response_model=Ingredient)
def update_ingredient(ingredient_id: int = fastapi.Path(), patch_ingredient_input_model: PatchIngredientInputModel = fastapi.Body()):

    """Update ingredient

    :param ingredient_id: Identifier for ingredient
    :type int
    ...
    :raises HTTPException: Raised if ingredient with ingredient_id not found
    ...
    :return: Updated ingredient
    :rtype: Ingredient
    """

    try:
        return features.ingredients_api.operations.update_ingredient(ingredient_id=ingredient_id, **patch_ingredient_input_model.model_dump())

    except features.ingredients_api.exceptions.IngredientNameViolationException:

        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST
        )

@ingredients_router.patch('/{ingredient_id', response_model=Ingredient)
def soft_delete_ingredient(ingredient_id: int = fastapi.Path()):

    """Soft delete ingredient

    :param ingredient_id: Identifier for ingredient
    :type int
    ...
    :raises HTTPException: Raised if ingredient with ingredient_id not found
    ...
    :return: Found ingredient
    :rtype: Ingredient
    """

    try:
        return features.ingredients_api.operations.soft_delete_ingredient(ingredient_id=ingredient_id)

    except features.ingredients_api.exceptions.IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST
        )

