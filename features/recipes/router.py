"""Recipes feature endpoints"""

import fastapi

import features.recipes
from .input_models import UpgradeRecipeInputModel
import features.recipes.operations
from features.recipes.responses import Category
import features.recipes.exceptions
from .input_models import (
    PatchCategoryInputModel,
    CreateCategoryInputModel,
    CreateRecipeInputModel,
)
from .responses import Recipe

categories_router = fastapi.APIRouter()
recipes_router = fastapi.APIRouter()


@categories_router.get("/", response_model=list[Category])
def get_all_categories():
    """
    Get all categories
    :return:
    """

    return features.recipes.operations.get_all_recipe_categories()


@categories_router.get("/{category_id}", response_model=Category)
def get_category(category_id: int = fastapi.Path()):
    """
    Get category

    :param category_id:
    :return:
    """

    try:
        return features.recipes.operations.get_category_by_id(category_id)
    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with {category_id=} does not exist",
        )


@categories_router.post("/", response_model=Category)
def create_category(create_category_input_model: CreateCategoryInputModel):
    """
    Crate category

    :param create_category_input_model:
    :return:
    """

    try:
        return features.recipes.operations.create_category(
            create_category_input_model.name
        )
    except features.recipes.exceptions.CategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {create_category_input_model.name} already exists",
        )


@categories_router.patch("/{category_id}", response_model=Category)
def update_category(
    category_id: int = fastapi.Path(),
    patch_category_input_model: PatchCategoryInputModel = fastapi.Body(),
):
    """
    Update category

    :param category_id:
    :param patch_category_input_model:
    :return:
    """
    try:
        return features.recipes.operations.update_category(
            category_id=category_id, **patch_category_input_model.model_dump()
        )
    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist",
        )
    except features.recipes.exceptions.CategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {patch_category_input_model.name} already exists",
        )


@recipes_router.get("/", response_model=list[Recipe])
def get_all_recipes():
    """Get all recipes"""
    return features.recipes.operations.get_all_recipes()


@recipes_router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int = fastapi.Path()):
    """Get recipe"""

    try:
        return features.recipes.operations.get_recipe_by_id(recipe_id)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist",
        )


@recipes_router.post("/", response_model=Recipe)
def create_recipe(create_recipe_input_model: CreateRecipeInputModel):
    """
    Create recipe

    :param create_recipe_input_model:
    :return:
    """
    try:
        return features.recipes.operations.create_recipe(
            **create_recipe_input_model.model_dump()
        )

    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {create_recipe_input_model.category_id} does not exist",
        )


@recipes_router.patch("/{recipe_id}", response_model=Recipe)
def update_recipe(
    recipe_id: int = fastapi.Path(),
    upgrade_recipe_input_model: UpgradeRecipeInputModel = fastapi.Body(),
):
    """
    Update recipe

    :param recipe_id: Identifier for recipe
    :type recipe_id: int
    ...
    :raises fastapi.HTTPException: Recipe not found
    ...
    :return: Updated recipe
    :rtype: features.recipes.responses.Recipe
    """
    try:
        return features.recipes.operations.update_recipe(
            recipe_id=recipe_id, **upgrade_recipe_input_model.model_dump()
        )

    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist",
        )


@recipes_router.delete("/{recipe_id}", response_model=Recipe)
def delete_recipe(recipe_id: int, user_id: int = 1):
    """
    Delete recipe

    :param recipe_id
    :param user_id
    :return:
    """

    try:
        return features.recipes.operations.delete_recipe(
            recipe_id=recipe_id, deleted_by=user_id
        )
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist",
        )
