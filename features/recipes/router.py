"""Recipes feature endpoints"""
from typing import List, Optional

import fastapi

import common.authentication
import features.recipes.exceptions
import features.recipes.exceptions
import features.recipes.operations
import features.recipes.responses
import features.recipes.input_models

ingredients_categories_router = fastapi.APIRouter()
ingredients_router = fastapi.APIRouter()

from common.authentication import Authenticate, AuthenticatedUser
categories_router = fastapi.APIRouter()
recipes_router = fastapi.APIRouter()


@ingredients_categories_router.get("/", response_model=list[features.recipes.responses.IngredientCategory])
def get_all_ingredients_categories_endpoint() -> List[Optional[features.recipes.responses.IngredientCategory]]:
    """Get all ingredients categories
    ...
    :return: list of ingredients categories
    :rtype: List[Ingredient]
    """

    return features.recipes.operations.get_all_ingredients_category()


@ingredients_categories_router.get("/{category_id}")
def get_ingredient_category_by_id(category_id: int = fastapi.Path()) -> features.recipes.responses.IngredientCategory:
    """Get ingredient category by id
    ...
    :return: ingredient category
    :rtype: IngredientCategory
    """

    try:
        return get_ingredient_category_by_id(category_id)
    except features.recipes.exceptions.IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient category with {category_id=} not found",
        )


@ingredients_categories_router.post("/")
def create_ingredient_category(
    created_category_input_model: features.recipes.input_models.CreateIngredientInputModel,
) -> features.recipes.responses.IngredientCategory:
    """Create ingredient category
    ...
    :return: created ingredient category
    :rtype: IngredientCategory
    """

    try:
        return create_ingredient_category(
            created_category_input_model.name, created_category_input_model.created_by
        )
    except features.recipes.exceptions.IngredientCategoryNameViolation:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient category with name {created_category_input_model.name} already exists",
        )


@ingredients_categories_router.patch("/{category_id}")
def patch_ingredient_category(
    category_id: int = fastapi.Path(),
    patch_ingredient_category_input_model: features.recipes.input_models.PatchIngredientCategoryInputModel = fastapi.Body(),
) -> features.recipes.input_models.PatchIngredientCategoryInputModel:
    """Patch ingredient category
    ...
    :return: updated ingredient category
    :rtype: IngredientCategory
    """

    try:
        return patch_ingredient_category_input_model(
            category_id, **patch_ingredient_category_input_model.model_dump()
        )
    except features.recipes.exceptions.IngredientCategoryIntegrityViolation:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST)


@ingredients_categories_router.delete("/{category_id", response_model=features.recipes.responses.IngredientCategory)
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
        return get_ingredient_category_by_id(
            category_id=category_id
        )
    except features.recipes.exceptions.IngredientCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with f'{category_id}' id does not exist",
        )


@ingredients_router.get("/", response_model=List[features.recipes.responses.Ingredient])
def get_all_ingredients_endpoint():
    """Get all ingredients
    ...
    :return: list of ingredients
    :rtype: List[Ingredient]
    """

    return features.recipes.operations.get_all_ingredients()


@ingredients_router.get("/{ingredient_id}", response_model=features.recipes.responses.Ingredient)
def get_ingredient(ingredient_id: int = fastapi.Path()):
    """Get ingredient

    :param ingredient_id: Identifier for ingredient
    ...
    :raises HTTPException: Raised if ingredient with ingredient_id not found
    ...
    :return: Found ingredient
    :rtype: Ingredient
    """

    try:
        return get_ingredient(ingredient_id)
    except features.recipes.exceptions.IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with {ingredient_id} not found",
        )


@ingredients_router.post("/", response_model=features.recipes.responses.Ingredient)
def create_ingredient(create_ingredient_input_model: features.recipes.input_models.CreateIngredientInputModel):
    """Create ingredient

    :param : name of ingredient
    ...
    :param : category of ingredient
    ...
    :param : calories of ingredient
    ...
    :param : carbo of ingredient
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
        return create_ingredient(
            features.recipes.input_models.CreateIngredientInputModel.name
        )

    except features.recipes.exceptions.IngredientNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name {create_ingredient_input_model.name} already exists",
        )


@ingredients_router.put("/{ingredient_id}", response_model=features.recipes.responses.Ingredient)
def update_ingredient(
    ingredient_id: int = fastapi.Path(),
    update_ingredient_input_model: features.recipes.input_models.UpdateIngredientInputModel = fastapi.Body(),
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
        return update_ingredient(
            ingredient_id=ingredient_id, **update_ingredient_input_model.model_dump()
        )

    except features.recipes.exceptions.IngredientNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id.name}' name not found",
        )

@ingredients_router.patch("/{ingredient_id}", response_model=features.recipes.responses.Ingredient)
def patch_ingredient(
    ingredient_id: int = fastapi.Path(),
    patch_ingredient_input_model: features.recipes.input_models.PatchIngredientInputModel = fastapi.Body(),
):
    """Patch ingredient

    :param ingredient_id: Identifier for ingredient
    :type int
    ...
    :raises HTTPException: Raised if ingredient with ingredient_id not found
    ...
    :return: Updated ingredient
    :rtype: Ingredient
    """

    try:
        return patch_ingredient(
            ingredient_id=ingredient_id, **patch_ingredient_input_model.model_dump()
        )

    except features.recipes.exceptions.IngredientNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id.name}' name not found",
        )

@ingredients_router.delete("/{ingredient_id", response_model=features.recipes.responses.Ingredient)
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
        return delete_ingredient(
            ingredient_id=ingredient_id
        )

    except features.recipes.exceptions.IngredientNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with f'{ingredient_id}' id does not exist",
        )


@recipes_categories_router.get('/', response_model=list[features.recipes.responses.RecipeCategory])
def get_all_categories():
    """
    Get all recipe categories
    :return:
    """

    return features.recipes.operations.get_all_recipe_categories()


@recipes_categories_router.get('/{category_id}', response_model=features.recipes.responses.RecipeCategory)
def get_category(category_id: int = fastapi.Path()):
    """
    Get recipe category

    :param category_id:
    :return:
    """

    try:
        return features.recipes.operations.get_category_by_id(category_id)
    except features.recipes.exceptions.RecipesCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with {category_id=} does not exist"
        )


@recipes_categories_router.post('/', response_model=features.recipes.responses.RecipeCategory)
def create_category(create_category_input_model: features.recipes.input_models.CreateRecipesCategoryInputModel):
    """
    Crate recipe category

    :param create_category_input_model:
    :return:
    """

    try:
        return features.recipes.operations.create_category(create_category_input_model.name)
    except features.recipes.exceptions.RecipesCategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {create_category_input_model.name} already exists"
        )


@recipes_categories_router.patch('/{category_id}', response_model=features.recipes.responses.RecipeCategory)
def update_category(category_id: int = fastapi.Path(),
                    patch_category_input_model: features.recipes.input_models.RecipesPatchCategoryInputModel = fastapi.Body()):
    """
    Update recipe category

    :param category_id:
    :param patch_category_input_model:
    :return:
    """
    try:
        return features.recipes.operations.update_category(category_id=category_id,
                                                           **patch_category_input_model.model_dump())
    except features.recipes.exceptions.RecipesCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist"
        )
    except features.recipes.exceptions.RecipesCategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {patch_category_input_model.name} already exists"
        )


@recipes_router.get('/', response_model=list[features.recipes.responses.Recipe])
def get_all_recipes():
    """Get all recipes"""
    return features.recipes.operations.get_all_recipes()


@recipes_router.get('/{recipe_id}', response_model=features.recipes.responses.Recipe)
def get_recipe(recipe_id: int = fastapi.Path()):
    """Get recipe"""

    try:
        return features.recipes.operations.get_recipe_by_id(recipe_id)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist"
        )


@recipes_router.post('/', response_model=features.recipes.responses.Recipe)
def create_recipe(create_recipe_input_model: features.recipes.input_models.CreateRecipeInputModel):
    """
    Create recipe

    :param create_recipe_input_model:
    :return:
    """
    try:
        return features.recipes.operations.create_recipe(**create_recipe_input_model.__dict__)

    except features.recipes.exceptions.RecipesCategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {create_recipe_input_model.category_id} does not exist"
        )


@recipes_router.patch('/{recipe_id}/instructions/{instruction_id}', response_model=features.recipes.responses.InstructionResponse)
def update_instructions(recipe_id: int = fastapi.Path(),
                        instruction_id: int = fastapi.Path(),
                        patch_instruction_input_model: features.recipes.input_models.PatchInstructionInputModel = fastapi.Body()):
    """
    Update instructions

    :param recipe_id:
    :param instruction_id:
    :param patch_instruction_input_model:
    :return:
    """
    try:
        updated_instruction = features.recipes.operations.update_instruction(
            recipe_id, instruction_id, **patch_instruction_input_model.model_dump()
        )
        return updated_instruction
    except features.recipes.exceptions.InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {instruction_id} does not exist"
        )
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist"
        )
    except features.recipes.exceptions.RecipeWithInstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Combination of {recipe_id=} and {instruction_id=} does not exist"
        )


@recipes_router.post('/{recipe_id}/instructions/', response_model=features.recipes.responses.InstructionResponse)
def create_instruction(recipe_id: int = fastapi.Path(),
                       create_instruction_input_model: features.recipes.input_models.CreateInstructionInputModel = fastapi.Body()):
    """
    Create instructions

    :param recipe_id:
    :param create_instruction_input_model:
    :return:
    """
    try:
        updated_instruction = features.recipes.operations.create_instruction(
            recipe_id, create_instruction_input_model
        )
        return updated_instruction
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist"
        )


@recipes_router.delete('/{recipe_id}/instructions/{instruction_id}', status_code=fastapi.status.HTTP_204_NO_CONTENT)
def delete_instruction(recipe_id: int = fastapi.Path(), instruction_id: int = fastapi.Path()):
    """
    Delete instruction

    :param recipe_id:
    :param instruction_id:
    :return:
    """
    try:
        features.recipes.operations.delete_instruction(recipe_id, instruction_id)
    except features.recipes.exceptions.InstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Instruction with id {instruction_id} does not exist"
        )
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} does not exist"
        )
    except features.recipes.exceptions.RecipeWithInstructionNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Combination of {recipe_id=} and {instruction_id=} does not exist"
        )


@recipes_router.delete('/{recipe_id}', response_model=features.recipes.responses.Recipe)
def delete_recipe(recipe_id: int, user_id: int = 1):
    """
    Delete recipe

    :param recipe_id
    :param user_id
    :return:
    """

    try:
        return features.recipes.operations.delete_recipe(recipe_id=recipe_id, deleted_by=user_id)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist"
        )
