"""Recipes feature endpoints"""

import fastapi

import common.authentication
import features.recipes.exceptions
import features.recipes.exceptions
import features.recipes.operations
import features.recipes.responses
from features.recipes.responses import Category
from features.recipes.responses import InstructionResponse, PSFRecipesResponseModel
from .input_models import (
    PatchCategoryInputModel,
    CreateCategoryInputModel,
    RecipeInputModel,
    PSFRecipesInputModel,
    PatchRecipeInputModel
)
from .input_models import PatchInstructionInputModel, CreateInstructionInputModel
from .responses import RecipeResponse
from typing import Annotated, Optional

categories_router = fastapi.APIRouter()
recipes_router = fastapi.APIRouter()


def _common_parameters(
    page: int = 1,
    page_size: int = 10,
    sort: Optional[str] = None,
    filters: Optional[str] = None,
):
    return PSFRecipesInputModel(**locals())


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
def create_category(
    create_category_input_model: CreateCategoryInputModel,
    user: Annotated[
        common.authentication.AuthenticatedUser,
        fastapi.Depends(common.authentication.admin),
    ],
):
    """
    Crate category

    :param create_category_input_model:
    :param user:
    :return:
    """

    try:
        return features.recipes.operations.create_category(create_category_input_model.name, created_by=user.id)
    except features.recipes.exceptions.CategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {create_category_input_model.name} already exists",
        )


@categories_router.patch("/{category_id}", response_model=Category)
def update_category(
    user: Annotated[
        common.authentication.AuthenticatedUser,
        fastapi.Depends(common.authentication.admin),
    ],
    category_id: int = fastapi.Path(),
    patch_category_input_model: PatchCategoryInputModel = fastapi.Body(),
):
    """
    Update category

    :param user:
    :param category_id:
    :param patch_category_input_model:
    :return:
    """
    try:
        return features.recipes.operations.update_category(
            category_id=category_id,
            **patch_category_input_model.model_dump(),
            updated_by=user.id,
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


@recipes_router.get("/", response_model=PSFRecipesResponseModel)
def get_all_recipes(
    paginated_input_model: Annotated[PSFRecipesInputModel, fastapi.Depends(_common_parameters)],
    user: common.authentication.optional_user,
):
    """
    Get all recipes
    :param paginated_input_model:
    :param user:
    """

    return features.recipes.operations.get_all_recipes(paginated_input_model, user=user)


@recipes_router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(user: common.authentication.optional_user, recipe_id: int = fastapi.Path()):
    """Get recipe"""

    try:
        return features.recipes.operations.get_recipe_by_id(recipe_id, user)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist",
        )


@recipes_router.post("/", response_model=RecipeResponse)
def create_recipe(
    create_recipe_input_model: RecipeInputModel,
    created_by: common.authentication.authenticated_user,
):
    """
    Create recipe

    :param create_recipe_input_model:
    :param created_by:
    :return:
    """
    try:
        return features.recipes.operations.create_recipe(**create_recipe_input_model.__dict__, created_by=created_by.id)

    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {create_recipe_input_model.category_id} does not exist",
        )


@recipes_router.patch("/{recipe_id}/instructions/{instruction_id}", response_model=InstructionResponse)
def update_instructions(
    user: common.authentication.authenticated_user,
    recipe_id: int = fastapi.Path(),
    instruction_id: int = fastapi.Path(),
    patch_instruction_input_model: PatchInstructionInputModel = fastapi.Body(),
):
    """
    Update instructions
    :param user:
    :param recipe_id:
    :param instruction_id:
    :param patch_instruction_input_model:
    :return:
    """
    try:
        updated_instruction = features.recipes.operations.update_instruction(
            recipe_id, instruction_id, **patch_instruction_input_model.model_dump(), user=user
        )
        return updated_instruction
    except features.recipes.exceptions.InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {instruction_id} does not exist",
        )
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist",
        )
    except features.recipes.exceptions.RecipeWithInstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Combination of {recipe_id=} and {instruction_id=} does not exist",
        )


@recipes_router.post("/{recipe_id}/instructions/", response_model=InstructionResponse)
def create_instruction(
    user: common.authentication.authenticated_user,
    recipe_id: int = fastapi.Path(),
    create_instruction_input_model: CreateInstructionInputModel = fastapi.Body(),
):
    """
    Create instructions

    :param user:
    :param recipe_id:
    :param create_instruction_input_model:
    :return:
    """
    try:
        updated_instruction = features.recipes.operations.create_instruction(
            recipe_id, create_instruction_input_model, user=user
        )
        return updated_instruction
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist",
        )


@recipes_router.delete(
    "/{recipe_id}/instructions/{instruction_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
def delete_instruction(
    user: common.authentication.authenticated_user,
    recipe_id: int = fastapi.Path(),
    instruction_id: int = fastapi.Path(),
):
    """
    Delete instruction

    :param user:
    :param recipe_id:
    :param instruction_id:
    :return:
    """
    try:
        features.recipes.operations.delete_instruction(recipe_id, instruction_id, user)
    except features.recipes.exceptions.InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {instruction_id} does not exist",
        )
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist",
        )
    except features.recipes.exceptions.RecipeWithInstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Combination of {recipe_id=} and {instruction_id=} does not exist",
        )


@recipes_router.delete("/{recipe_id}", response_model=RecipeResponse)
def delete_recipe(recipe_id: int, user: common.authentication.authenticated_user):
    """
    Delete recipe

    :param recipe_id
    :param user
    :return:
    """

    try:
        return features.recipes.operations.delete_recipe(recipe_id=recipe_id, deleted_by=user)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist",
        )


@recipes_router.put('/{recipe_id}', response_model=RecipeResponse)
def update_recipe(recipe_id: int = fastapi.Path(),
                 update_recipe_input_model:  RecipeInputModel = fastapi.Body()):

    """
    Update recipe

    :param recipe_id:
    :param update_recipe_input_model:
    :return:
    """

    try:
        return features.recipes.operations.update_recipe(recipe_id=recipe_id)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist"
        )

    except features.recipes.exceptions.InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {update_recipe_input_model.instruction_id} does not exist"
        )

    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {update_recipe_input_model.category_id} does not exist"
        )


@recipes_router.patch('/{recipe_id}', response_model=RecipeResponse)
def patch_recipe(recipe_id: int = fastapi.Path(),
                patch_recipe_input_model: PatchRecipeInputModel = fastapi.Body()):

    """
    Update recipe

    :param recipe_id:
    :param patch_recipe_input_model:
    :return:
    """

    try:
        return features.recipes.operations.patch_recipe(recipe_id=recipe_id,
                                                         **patch_recipe_input_model.model_dump())

    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist"
        )
