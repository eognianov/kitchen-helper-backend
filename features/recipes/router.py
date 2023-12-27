"""Recipes feature endpoints"""

import fastapi

import common.authentication

from features.recipes.responses import RecipeResponse, IngredientCategory, RecipeCategory, IngredientResponse
from features.recipes.responses import InstructionResponse, PSFRecipesResponseModel, CategoryShortResponse

from .input_models import (
    RecipesPatchCategoryInputModel,
    CreateRecipesCategoryInputModel,
    CreateRecipeInputModel,
    PSFRecipesInputModel,
    IngredientInputModel,
    PatchIngredientCategoryInputModel,
    PatchIngredientInputModel,
    PatchInstructionInputModel,
    CreateInstructionInputModel,
)

from features.recipes.operations import (
    get_all_ingredients_category,
    get_all_ingredients,
    get_all_recipe_categories,
    get_recipe_category_by_id,
    get_recipe_by_id,
    update_instruction,
    get_ingredient_by_id,
)

from features.recipes.exceptions import (
    IngredientCategoryNameViolation,
    IngredientCategoryNotFoundException,
    IngredientCategoryIntegrityViolation,
    IngredientNotFoundException,
    IngredientNameViolationException,
    RecipesCategoryNotFoundException,
    RecipesCategoryNameViolationException,
    RecipeNotFoundException,
    InstructionNotFoundException,
    RecipeWithInstructionNotFoundException,
)

from typing import Annotated, Optional

ingredients_categories_router = fastapi.APIRouter()
ingredients_router = fastapi.APIRouter()

from common.authentication import Authenticate, AuthenticatedUser

recipes_categories_router = fastapi.APIRouter()
recipes_router = fastapi.APIRouter()


def _common_parameters(
    page: int = 1,
    page_size: int = 10,
    sort: Optional[str] = None,
    filters: Optional[str] = None,
):
    return PSFRecipesInputModel(**locals())


@ingredients_categories_router.get("/", response_model=list[IngredientCategory])
def get_all_ingredients_categories_endpoint():
    """
    Get all ingredients categories
    :return:
    """

    return get_all_ingredients_category()


@ingredients_categories_router.get("/{category_id}", response_model=IngredientCategory)
def get_ingredient_category_by_id(category_id: int = fastapi.Path()):
    """Get ingredient category by id
    ...
    :return: ingredient category
    :rtype: IngredientCategory
    """

    try:
        return get_ingredient_category_by_id(category_id)
    except IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient category with {category_id=} not found",
        )


@ingredients_categories_router.delete("/{category_id", response_model=IngredientCategory)
def delete_category(category_id: int = fastapi.Path()):
    """Delete ingredient category

    :param category_id: Identifier for category
    ...
    :raises HTTPException: Raised if category with category_id not found
    ...
    :return: Found category
    :rtype: IngredientCategory
    """

    try:
        return get_ingredient_category_by_id(category_id=category_id)
    except IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with f'{category_id}' id does not exist",
        )


@ingredients_router.get("/")
def get_all_ingredients_endpoint(user: common.authentication.optional_user):
    """
    Get all ingredients
    :param user:
    :return:
    """

    return get_all_ingredients(user=user)


@ingredients_router.get("/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(user: common.authentication.optional_user, ingredient_id: int = fastapi.Path()):
    """
    Get ingredient
    :param user:
    :param ingredient_id:
    :return:
    """

    try:
        return get_ingredient_by_id(ingredient_id, user)
    except IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with {ingredient_id} not found",
        )


@ingredients_router.post("/", response_model=IngredientResponse)
def create_ingredient(
    create_ingredient_input_model: IngredientInputModel, created_by: common.authentication.authenticated_user
):
    """
    Create ingredient
    :param create_ingredient_input_model:
    :param created_by:
    :return:
    """

    try:
        return create_ingredient(**create_ingredient_input_model.__dict__, created_by=created_by.id)

    except IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name {create_ingredient_input_model.name} already exists",
        )


# TODO: Make working update router
@ingredients_router.put("/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(
    ingredient_id: int = fastapi.Path(),
    update_ingredient_input_model: IngredientInputModel = fastapi.Body(),
):
    """
    Update ingredient
    :param ingredient_id:
    :param update_ingredient_input_model:
    :return:
    """

    try:
        return update_ingredient(ingredient_id=ingredient_id, **update_ingredient_input_model.model_dump())

    except IngredientNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id}' id not found",
        )


# TODO: Make working delete ingredient router
@ingredients_router.delete("/{ingredient_id", response_model=IngredientResponse)
def delete_ingredient(ingredient_id: int = fastapi.Path()):
    """Soft delete ingredient

    :param ingredient_id: Identifier for ingredient
    ...
    :raises HTTPException: Raised if ingredient with ingredient_id not found
    ...
    :return: Found ingredient
    :rtype: Ingredient
    """

    try:
        return delete_ingredient(ingredient_id=ingredient_id)

    except IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id}' id does not exist",
        )


@recipes_categories_router.get('/', response_model=list[RecipeCategory])
def get_all_categories():
    """
    Get all recipe categories
    :return:
    """

    return get_all_recipe_categories()


@recipes_categories_router.get("/{category_id}", response_model=RecipeCategory)
def get_category(category_id: int = fastapi.Path()):
    """
    Get recipe category

    :param category_id:
    :return:
    """

    try:
        return get_recipe_category_by_id(category_id)
    except RecipesCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with {category_id=} does not exist",
        )


@recipes_categories_router.post("/", response_model=CategoryShortResponse)
def create_category(
    create_category_input_model: CreateRecipesCategoryInputModel,
    user: Annotated[
        common.authentication.AuthenticatedUser,
        fastapi.Depends(common.authentication.admin),
    ],
):
    """
    Crate recipe category

    :param create_category_input_model:
    :param user:
    :return:
    """

    try:
        return create_category(create_category_input_model.name, created_by=user.id)
    except RecipesCategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {create_category_input_model.name} already exists",
        )


@recipes_categories_router.patch("/{category_id}", response_model=RecipeCategory)
def update_category(
    user: Annotated[
        common.authentication.AuthenticatedUser,
        fastapi.Depends(common.authentication.admin),
    ],
    category_id: int = fastapi.Path(),
    patch_category_input_model: RecipesPatchCategoryInputModel = fastapi.Body(),
):
    """
    Update recipe category

    :param user:
    :param category_id:
    :param patch_category_input_model:
    :return:
    """
    try:
        return update_category(
            category_id=category_id,
            **patch_category_input_model.model_dump(),
            updated_by=user.id,
        )
    except RecipesCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist",
        )
    except RecipesCategoryNameViolationException:
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

    return get_all_recipes(paginated_input_model, user=user)


@recipes_router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(user: common.authentication.optional_user, recipe_id: int = fastapi.Path()):
    """Get recipe"""

    try:
        return get_recipe_by_id(recipe_id, user)
    except RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist",
        )


@recipes_router.post("/", response_model=RecipeResponse)
def create_recipe(
    create_recipe_input_model: CreateRecipeInputModel,
    created_by: common.authentication.authenticated_user,
):
    """
    Create recipe

    :param create_recipe_input_model:
    :param created_by:
    :return:
    """
    try:
        return create_recipe(**create_recipe_input_model.__dict__, created_by=created_by.id)

    except RecipesCategoryNotFoundException:
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
        updated_instruction = update_instruction(
            recipe_id, instruction_id, **patch_instruction_input_model.model_dump(), user=user
        )
        return updated_instruction
    except InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {instruction_id} does not exist",
        )
    except RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist",
        )
    except RecipeWithInstructionNotFoundException:
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
        updated_instruction = create_instruction(recipe_id, create_instruction_input_model, user=user)
        return updated_instruction
    except RecipeNotFoundException:
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
        delete_instruction(recipe_id, instruction_id, user)
    except InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {instruction_id} does not exist",
        )
    except RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist",
        )
    except RecipeWithInstructionNotFoundException:
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
        return delete_recipe(recipe_id=recipe_id, deleted_by=user)
    except RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist",
        )
