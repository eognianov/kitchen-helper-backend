"""Recipes feature endpoints"""

import fastapi

import features.recipes.exceptions
import features.recipes.operations
import features.recipes.responses
from features.recipes.responses import InstructionResponse
from .input_models import PatchCategoryInputModel, CreateCategoryInputModel, CreateRecipeInputModel, \
    UpdateInstructionInputModel, PatchInstructionInputModel, CreateInstructionInputModel

categories_router = fastapi.APIRouter()
recipes_router = fastapi.APIRouter()


@categories_router.get('/')
def get_all_categories():
    """
    Get all categories
    :return:
    """

    categories = features.recipes.operations.get_all_recipe_categories()

    return [features.recipes.responses.Category(**_.__dict__) for _ in categories]


@categories_router.get('/{category_id}')
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
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Category with {category_id=} does not exist"
        )


@categories_router.post('/')
def create_category(create_category_input_model: CreateCategoryInputModel):
    """
    Crate category

    :param create_category_input_model:
    :return:
    """

    try:
        created_category = features.recipes.operations.create_category(create_category_input_model.name)
        return features.recipes.responses.Category(**created_category.__dict__)
    except features.recipes.exceptions.CategoryNameViolationException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name {create_category_input_model.name} already exists"
        )


@categories_router.patch('/{category_id}')
def update_category(category_id: int = fastapi.Path(),
                    patch_category_input_model: PatchCategoryInputModel = fastapi.Body()):
    """
    Update category

    :param category_id:
    :param patch_category_input_model:
    :return:
    """
    try:
        updated_category = features.recipes.operations.update_category(category_id,
                                                                       **patch_category_input_model.model_dump())
        return features.recipes.responses.Category(**updated_category.__dict__)
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


@recipes_router.get('/')
def get_all_recipes():
    """Get all recipes"""
    all_recipes = features.recipes.operations.get_all_recipes()
    return [features.recipes.responses.Recipe(**_.__dict__) for _ in all_recipes]


@recipes_router.get('/{recipe_id}')
def get_recipe(recipe_id: int = fastapi.Path()):
    """Get recipe"""

    try:
        recipe = features.recipes.operations.get_recipe_by_id(recipe_id)
        return features.recipes.responses.Recipe(**recipe.__dict__)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist"
        )


@recipes_router.post('/')
def create_recipe(create_recipe_input_model: CreateRecipeInputModel):
    """
    Create recipe

    :param create_recipe_input_model:
    :return:
    """
    try:
        created_recipe = features.recipes.operations.create_recipe(**create_recipe_input_model.__dict__)

        return features.recipes.responses.Recipe(**created_recipe.__dict__)
    except features.recipes.exceptions.CategoryNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {create_recipe_input_model.category_id} does not exist"
        )


@recipes_router.put('/{recipe_id}/instructions',
                    status_code=fastapi.status.HTTP_201_CREATED,
                    response_model=list[InstructionResponse])
def update_instructions(instructions_request: list[UpdateInstructionInputModel], recipe_id: int):
    """
    Update instructions for recipe

    :param instructions_request:
    :param recipe_id:
    :return:
    """

    try:
        instructions = features.recipes.operations.update_instructions(instructions_request, recipe_id)
    except features.recipes.exceptions.RecipeNotFoundException:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with {recipe_id=} does not exist"
        )

    return instructions


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
def create_instructions(recipe_id: int = fastapi.Path(),
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
