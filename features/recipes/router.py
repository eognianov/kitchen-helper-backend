"""Recipes feature endpoints"""

import fastapi

import features.recipes.exceptions
import features.recipes.operations
import features.recipes.responses
from features.recipes.responses import Category
from features.recipes.responses import InstructionResponse, PageResponse, RecipeResponse
from .input_models import PatchCategoryInputModel, CreateCategoryInputModel, CreateRecipeInputModel
from .input_models import PatchInstructionInputModel, CreateInstructionInputModel

categories_router = fastapi.APIRouter()
recipes_router = fastapi.APIRouter()


@categories_router.get('/', response_model=list[Category])
def get_all_categories():
    """
    Get all categories
    :return:
    """

    return features.recipes.operations.get_all_recipe_categories()


@categories_router.get('/{category_id}', response_model=Category)
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
            detail=f"Category with {category_id=} does not exist"
        )


@categories_router.post('/', response_model=Category)
def create_category(create_category_input_model: CreateCategoryInputModel):
    """
    Crate category

    :param create_category_input_model:
    :return:
    """

    try:
        return features.recipes.operations.create_category(create_category_input_model.name)
    except features.recipes.exceptions.CategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {create_category_input_model.name} already exists"
        )


@categories_router.patch('/{category_id}', response_model=Category)
def update_category(category_id: int = fastapi.Path(),
                    patch_category_input_model: PatchCategoryInputModel = fastapi.Body()):
    """
    Update category

    :param category_id:
    :param patch_category_input_model:
    :return:
    """
    try:
        return features.recipes.operations.update_category(category_id=category_id,
                                                           **patch_category_input_model.model_dump())
    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} does not exist"
        )
    except features.recipes.exceptions.CategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {patch_category_input_model.name} already exists"
        )


@recipes_router.get('/', response_model=PageResponse)
def get_all_recipes(
        page_num: int = fastapi.Query(default=1, gt=0, description="Page number"),
        page_size: int = fastapi.Query(default=10, gt=0, description="Items per page"),
        sort: str = fastapi.Query(None, description="Sort criteria: category.name-asc,complexity-desc"),
        filters: str = fastapi.Query(None,
                                     description="Filters criteria: category=category1*category2,time_to_prepare=1-100,"
                                                 "complexity=1-5,created_by=1"),
        # category: str = fastapi.Query(None, description="Filter by category: category1,category2"),
        # time_to_prepare: str = fastapi.Query(None, description="Filter by time to prepare range: 0,200"),
        # complexity: str = fastapi.Query(None, description="Filter by complexity range: 1,5")
):
    """
    Get all recipes

    :param page_num:
    :param page_size:
    :param sort:
    :param filters:
    """

    try:
        return features.recipes.operations.get_all_recipes(page_num=page_num, page_size=page_size, sort=sort,
                                                           filters=filters)
    except features.recipes.exceptions.InvalidPageNumber:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Invalid page number"
        )
    except features.recipes.exceptions.InvalidSortDirection:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Invalid ordering direction"
        )
    except features.recipes.exceptions.InvalidColumn:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Invalid ordering column"
        )
    except features.recipes.exceptions.InvalidRange:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Invalid filter entry"
        )


@recipes_router.get('/{recipe_id}', response_model=RecipeResponse)
def get_recipe(recipe_id: int = fastapi.Path()):
    """Get recipe"""

    try:
        return features.recipes.operations.get_recipe_by_id(recipe_id)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist"
        )


@recipes_router.post('/', response_model=RecipeResponse)
def create_recipe(create_recipe_input_model: CreateRecipeInputModel):
    """
    Create recipe

    :param create_recipe_input_model:
    :return:
    """
    try:
        return features.recipes.operations.create_recipe(**create_recipe_input_model.__dict__)

    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {create_recipe_input_model.category_id} does not exist"
        )


@recipes_router.patch('/{recipe_id}/instructions/{instruction_id}', response_model=InstructionResponse)
def update_instructions(recipe_id: int = fastapi.Path(),
                        instruction_id: int = fastapi.Path(),
                        patch_instruction_input_model: PatchInstructionInputModel = fastapi.Body()):
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


@recipes_router.post('/{recipe_id}/instructions/', response_model=InstructionResponse)
def create_instruction(recipe_id: int = fastapi.Path(),
                       create_instruction_input_model: CreateInstructionInputModel = fastapi.Body()):
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
def delete_instruction(recipe_id: int = fastapi.Path(), instruction_id=fastapi.Path()):
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


@recipes_router.delete('/{recipe_id}', response_model=RecipeResponse)
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
