"""Ingredients feature endpoints"""
from typing import List

import fastapi
from features.recipes.ingredients.operations import *
from features.recipes.ingredients.responses import IngredientCategory
import features.recipes.ingredients.exceptions
from .input_models import (
    PatchIngredientInputModel,
    CreateIngredientInputModel,
    PatchIngredientCategoryInputModel,
)

categories_router = fastapi.APIRouter()
ingredients_router = fastapi.APIRouter()


@categories_router.get("/")
def get_all_ingredients_categories_endpoint() -> List[Ingredient]:
    """Get all ingredients categories
    ...
    :return: list of ingredients categories
    :rtype: List[Ingredient]
    """

    return features.ingredients_api.operations.get_all_ingredients_category()


@categories_router.get("/{category_id}")
def get_ingredient_category_by_id(category_id: int = fastapi.Path()) -> Ingredient:
    """Get ingredient category by id
    ...
    :return: ingredient category
    :rtype: IngredientCategory
    """

    try:
        return features.ingredients_api.operations.get_ingredient_category(category_id)
    except features.ingredients_api.exceptions.IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient category with {category_id=} not found",
        )


@categories_router.post("/")
def create_ingredient_category(
    created_category_input_model: IngredientCategory,
) -> IngredientCategory:
    """Create ingredient category
    ...
    :return: created ingredient category
    :rtype: IngredientCategory
    """

    try:
        return features.ingredients_api.operations.create_ingredient_category(
            created_category_input_model.name, created_category_input_model.created_by
        )
    except features.ingredients_api.exceptions.IngredientCategoryNameViolation:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient category with name {created_category_input_model.name} already exists",
        )


@categories_router.patch("/{category_id}")
def update_ingredient_category(
    category_id: int = fastapi.Path(),
    patch_ingredient_category_input_model: PatchIngredientCategoryInputModel = fastapi.Body(),
) -> IngredientCategory:
    """Update ingredient category
    ...
    :return: updated ingredient category
    :rtype: IngredientCategory
    """

    try:
        return features.ingredients_api.operations.update_ingredient_category(
            category_id, **patch_ingredient_category_input_model.model_dump()
        )
    except features.ingredients_api.exceptions.IngredientCategoryIntegrityViolation:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST)


@categories_router.delete("/{category_id", response_model=IngredientCategory)
def delete_category(category_id: int = fastapi.Path()):
    """Delete category

    :param category_id: Identifier for category
    :type int
    ...
    :raises HTTPException: Raised if category with category_id not found
    ...
    :return: Found category
    :rtype: IngredientCategory
    """

    try:
        return features.ingredients_api.operations.get_ingredient_category_by_id(
            category_id=category_id
        )
    except features.ingredients_api.exceptions.IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with f'{category_id}' id does not exist",
        )


@ingredients_router.get("/", response_model=List[Ingredient])
def get_all_ingredients_endpoint():
    """Get all ingredients
    ...
    :return: list of ingredients
    :rtype: List[Ingredient]
    """

    return features.ingredients_api.operations.get_all_ingredients()


@ingredients_router.get("/{ingredient_id}", response_model=Ingredient)
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
            detail=f"Ingredient with {ingredient_id} not found",
        )


@ingredients_router.post("/", response_model=Ingredient)
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
        return features.ingredients_api.operations.create_ingredient(
            create_ingredient_input_model.name
        )

    except features.ingredients_api.exceptions.IngredientNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name {create_ingredient_input_model.name} already exists",
        )


@ingredients_router.patch("/{ingredient_id", response_model=Ingredient)
def update_ingredient(
    ingredient_id: int = fastapi.Path(),
    patch_ingredient_input_model: PatchIngredientInputModel = fastapi.Body(),
):
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
        return features.ingredients_api.operations.update_ingredient(
            ingredient_id=ingredient_id, **patch_ingredient_input_model.model_dump()
        )

    except features.ingredients_api.exceptions.IngredientNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id.name}' name not found",
        )


@ingredients_router.delete("/{ingredient_id", response_model=Ingredient)
def delete_ingredient(ingredient_id: int = fastapi.Path()):
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
        return features.ingredients_api.operations.delete_ingredient(
            ingredient_id=ingredient_id
        )

    except features.ingredients_api.exceptions.IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id}' id does not exist",
        )
