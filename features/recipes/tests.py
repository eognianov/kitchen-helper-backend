import unittest.mock
import pytest
from fastapi.testclient import TestClient
from api import app
from pytest import fixture

import common.authentication
import db.connection
from tests.fixtures import use_test_db, admin, user
from features.recipes import operations
from features.recipes.models import RecipeCategory, RecipeInstruction, Recipe, IngredientCategory, Ingredient
from features.recipes.exceptions import (
    IngredientCategoryNameViolation,
    IngredientCategoryNotFoundException,
    IngredientNameViolationException,
    IngredientNotFoundException,
    RecipesCategoryNameViolationException,
    RecipesCategoryNotFoundException,
)
from features.recipes.input_models import CreateInstructionInputModel


@fixture
def bypass_published_filter(mocker):
    mocker.patch('features.recipes.operations._get_published_filter_expression', return_value=[])
    yield


class TestIngredientCategoryOperations:
    def test_create_ingredient_category_success(self, use_test_db, mocker):
        expected_name = "new_category"
        operations.create_ingredient_category(expected_name)

        with db.connection.get_session() as session:
            categories = session.query(IngredientCategory).all()

        assert len(categories) == 1
        assert categories[0].name == expected_name


def test_create_ingredient_category_with_existing_name(use_test_db):
    expected_name = "new_category"
    operations.create_ingredient_category(expected_name)

    with pytest.raises(IngredientCategoryNameViolation):
        operations.create_ingredient_category(expected_name)


def test_get_category_by_id_success():
    created_category = operations.create_ingredient_category("name")
    category_from_db = operations.get_ingredient_category_by_id(created_category.id)

    assert created_category.name == category_from_db.name
    assert created_category.created_by == category_from_db.created_by
    assert created_category.created_on == category_from_db.created_on


def test_get_category_by_id_not_fail():
    with pytest.raises(IngredientCategoryNotFoundException):
        operations.get_ingredient_category_by_id(1)


def test_get_all_categories():
    assert len(operations.get_all_ingredients_category()) == 0
    operations.create_ingredient_category("new")
    assert len(operations.get_all_ingredients_category()) == 1


def test_update_category():
    created_category = operations.create_ingredient_category("name")
    operations.update_ingredient_category(created_category.id, "name", "new_name")
    updated_category = operations.get_ingredient_category_by_id(created_category.id)
    assert updated_category.name == "new_name"


class TestIngredientOperations:
    def test_create_ingredient_operation(self):
        expected_name = "new_ingredient"
        operations.create_ingredient(expected_name)

        with db.connection.get_session() as session:
            ingredients = session.query(Ingredient).all()

        assert len(ingredients) == 1
        assert ingredients[0].name == expected_name

    def test_create_ingredient_with_existing_name(self):
        expected_name = "new_category"
        operations.create_ingredient(expected_name)

        with pytest.raises(IngredientNameViolationException):
            operations.create_ingredient(expected_name)

    def test_get_ingredient_by_id_success(self):
        created_ingredient = operations.create_ingredient("name")
        ingredient_from_db = operations.get_ingredient(created_ingredient.id)

        assert created_ingredient.name == ingredient_from_db.name
        assert created_ingredient.created_by == ingredient_from_db.created_by
        assert created_ingredient.created_on == ingredient_from_db.created_on

    def test_get_ingredient_by_id_not_fail(self):
        with pytest.raises(IngredientNotFoundException):
            operations.get_ingredient(1)

    def test_get_all_ingredients(self):
        assert len(operations.get_all_ingredients()) == 0
        operations.create_ingredient("new")
        assert len(operations.get_all_ingredients()) == 1

    def test_update_ingredient(self):
        created_ingredient = operations.create_ingredient("name")
        operations.update_ingredient(created_ingredient.id, "name", "new_name")
        updated_ingredient = operations.get_ingredient(created_ingredient.id)
        assert updated_ingredient.name == "new_name"


class TestIngredientsEndpoints:
    client = TestClient(app)

    @classmethod
    def test_get_all_ingredients_empty(cls, mocker):
        get_all_ingredients_spy = mocker.spy(operations, "get_all_ingredients")
        response = cls.client.get("/ingredients/")
        assert response.status_code == 200
        assert get_all_ingredients_spy.call_count == 1

    @classmethod
    def test_get_all_ingredients(cls, mocker):
        get_all_ingredients_spy = mocker.spy(operations, "get_all_ingredients")
        response = cls.client.get("/ingredients/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert get_all_ingredients_spy.call_count == 1

    @classmethod
    def test_get_ingredient_by_id(cls, mocker):
        created_ingredient = operations.create_ingredient("new")
        get_ingredient_spy = mocker.spy(operations, "get_ingredient_by_id")
        response = cls.client.get(f"/ingredients/{created_ingredient.id}")
        assert response.status_code == 200
        get_ingredient_spy.assert_called_with(created_ingredient.id)

    @classmethod
    def test_patch_ingredient(cls, mocker):
        created_ingredient = operations.create_ingredient("new")
        patch_payload = {"field": "name", "value": "updated"}
        update_ingredient_spy = mocker.spy(operations, "update_ingredient")
        response = cls.client.patch(f"/ingredients/{created_ingredient.id}", json=patch_payload)
        assert response.status_code == 200
        update_ingredient_spy.assert_called_with(ingredient_id=1, field="name", value="updated")


class TestCategoryOperations:
    def test_create_category_success(self, use_test_db, mocker):
        expected_name = "new_category"
        operations.create_category(expected_name, 1)
        with db.connection.get_session() as session:
            categories = session.query(RecipeCategory).all()
        assert len(categories) == 1
        assert categories[0].name == expected_name

    def test_create_category_with_existing_name(self, use_test_db):
        expected_name = "new_category"
        operations.create_category(expected_name, 1)
        with pytest.raises(RecipesCategoryNameViolationException):
            operations.create_category(expected_name, 1)

    def test_get_category_by_id_success(self, use_test_db):
        created_category = operations.create_category("name", 1)
        category_from_db = operations.get_category_by_id(created_category.id)

        assert created_category.name == category_from_db.name
        assert created_category.created_by == category_from_db.created_by
        assert created_category.created_on == category_from_db.created_on

    def test_get_category_by_id_not_fail(self, use_test_db):
        with pytest.raises(RecipesCategoryNotFoundException):
            operations.get_category_by_id(1)

    def test_get_all_categories(self, use_test_db):
        assert len(operations.get_all_recipe_categories()) == 0
        operations.create_category("new", 1)
        assert len(operations.get_all_recipe_categories()) == 1

    def test_update_category(self, use_test_db):
        created_category = operations.create_category("name", 1)
        operations.update_category(created_category.id, "name", "new_name", 1)
        updated_category = operations.get_category_by_id(created_category.id)
        assert updated_category.name == "new_name"


class TestCategoriesEndpoints:
    client = TestClient(app)

    @classmethod
    def test_get_all_categories_empty(cls, use_test_db, mocker):
        get_all_categories_spy = mocker.spy(operations, "get_all_recipe_categories")
        response = cls.client.get("/api/categories/")
        assert response.status_code == 200
        assert get_all_categories_spy.call_count == 1

    @classmethod
    def test_get_all_categories(cls, use_test_db, mocker):
        created_category = operations.create_category("new", 1)
        get_all_categories_spy = mocker.spy(operations, "get_all_recipe_categories")
        response = cls.client.get("/api/categories/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert get_all_categories_spy.call_count == 1

    @classmethod
    def test_get_category_by_id(cls, use_test_db, mocker):
        created_category = operations.create_category("new", 1)
        get_category_spy = mocker.spy(operations, "get_category_by_id")
        response = cls.client.get(f"/api/categories/{created_category.id}")
        assert response.status_code == 200
        get_category_spy.assert_called_with(created_category.id)

    @classmethod
    def test_patch_category(cls, use_test_db, mocker, admin):
        created_category = operations.create_category("new", 1)
        patch_payload = {"field": "name", "value": "updated"}
        update_category_spy = mocker.spy(operations, "update_category")
        response = cls.client.patch(
            f"/api/categories/{created_category.id}",
            json=patch_payload,
            headers={"Authorization": "Bearer token"},
        )
        assert response.status_code == 200
        update_category_spy.assert_called_with(category_id=1, field="name", value="updated", updated_by=1)


class TestInstructionsOperations:
    def setup(self):
        self.recipe = {
            "name": "name",
            "time_to_prepare": 0,
            "category_id": 1,
            "picture": "",
            "summary": "summary",
            "calories": 1,
            "carbo": 1,
            "fats": 1,
            "proteins": 1,
            "cholesterol": 1,
            "created_by": 1,
            "instructions": [],
        }

    def test_create_recipe_without_instructions_success(self, use_test_db):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()
        assert len(recipes) == 1
        assert len(recipe.instructions) == 0

    def test_create_recipe_with_instructions_success(self, use_test_db, bypass_published_filter):
        instruction = {
            "instruction": "instruction",
            "category": "Lunch",
            "time": 10,
            "complexity": 5,
        }
        instruction2 = {
            "instruction": "instruction",
            "category": "Lunch",
            "time": 10,
            "complexity": 4,
        }

        self.recipe["instructions"].append(CreateInstructionInputModel(**instruction))
        self.recipe["instructions"].append(CreateInstructionInputModel(**instruction2))

        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()
        assert len(recipes) == 1
        assert len(recipe.instructions) == 2
        assert recipes[0].time_to_prepare == 20
        assert recipes[0].complexity == 4.5
        assert recipes[0].instructions[0].category == "Lunch"

    def test_create_instruction_for_recipe_success(self, use_test_db, bypass_published_filter, user):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**new_instruction), user=user
        )

        with db.connection.get_session() as session:
            instructions = session.query(RecipeInstruction).all()
            instruction = session.query(RecipeInstruction).first()
            assert len(instructions) == 1
            assert instruction.instruction == new_instruction["instruction"]
            assert instruction.category == new_instruction["category"].capitalize()
            assert instruction.time == new_instruction["time"]
            assert instruction.complexity == new_instruction["complexity"]

    def test_get_instruction_by_id_success(self, use_test_db, bypass_published_filter, user=user):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**new_instruction), user=user
        )

        instruction = operations.get_instruction_by_id(instruction_id=1)
        assert instruction.instruction == new_instruction["instruction"]
        assert instruction.category == new_instruction["category"].capitalize()
        assert instruction.time == new_instruction["time"]
        assert instruction.complexity == new_instruction["complexity"]

    def test_update_instruction_success(self, use_test_db, bypass_published_filter, user):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        created_instruction = operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**new_instruction), user=user
        )
        operations.update_instruction(
            recipe_id=1, instruction_id=created_instruction.id, field="instruction", value="new_name", user=user
        )
        operations.update_instruction(
            recipe_id=1, instruction_id=created_instruction.id, field="category", value="Breakfast", user=user
        )
        operations.update_instruction(
            recipe_id=1, instruction_id=created_instruction.id, field="time", value="20", user=user
        )
        operations.update_instruction(
            recipe_id=1, instruction_id=created_instruction.id, field="complexity", value="1", user=user
        )
        updated_instruction = operations.get_instruction_by_id(created_instruction.id)
        assert updated_instruction.instruction == "new_name"
        assert updated_instruction.category == "Breakfast"
        assert updated_instruction.time == 20
        assert updated_instruction.complexity == 1

    def test_delete_instruction_success(self, use_test_db, bypass_published_filter, user):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }
        new_instruction2 = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**new_instruction), user=user
        )
        operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**new_instruction2), user=user
        )

        operations.delete_instruction(recipe_id=1, instruction_id=2, user=common.authentication.AuthenticatedUser(id=1))

        with db.connection.get_session() as session:
            instructions = session.query(RecipeInstruction).all()
        assert len(instructions) == 1


class TestInstructionsEndpoints:
    def setup(self):
        self.client = TestClient(app)
        self.recipe = {
            "name": "name",
            "time_to_prepare": 0,
            "category_id": 1,
            "picture": "",
            "summary": "summary",
            "calories": 1,
            "carbo": 1,
            "fats": 1,
            "proteins": 1,
            "cholesterol": 1,
            "created_by": 1,
            "instructions": [],
        }
        self.new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

    def test_patch_instruction_success(self, use_test_db, mocker, bypass_published_filter, user):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )

        patch_payload = {"field": "instruction", "value": "updated"}

        update_instruction_spy = mocker.spy(operations, "update_instruction")
        response = self.client.patch(
            f"/api/recipes/{created_recipe.id}/instructions/{created_instruction.id}",
            json=patch_payload,
            headers={'Authorization': 'Bearer token'},
        )
        assert response.status_code == 200
        update_instruction_spy.assert_called_with(
            recipe_id=1, instruction_id=1, field="instruction", value="updated", user=unittest.mock.ANY
        )

    def test_patch_instruction_with_wrong_field_fail(self, use_test_db, mocker, bypass_published_filter, user):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )

        patch_payload = {"field": "test", "value": "updated"}

        response = self.client.patch(
            f"/api/recipes/{created_recipe.id}/instructions/{created_instruction.id}",
            json=patch_payload,
            headers={'Authorization': 'Bearer token'},
        )
        assert response.status_code == 422

    def test_delete_instruction_success(self, use_test_db, mocker, bypass_published_filter, user):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )

        headers = {"Authorization": "Bearer token"}

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        response = self.client.delete(
            f"/api/recipes/{created_recipe.id}/instructions/{created_instruction.id}", headers=headers
        )
        assert response.status_code == 204
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=1, user=unittest.mock.ANY)

    def test_delete_instruction_with_non_existing_recipe_fail(self, use_test_db, mocker, bypass_published_filter, user):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        headers = {"Authorization": "Bearer token"}
        response = self.client.delete(f"/api/recipes/{2}/instructions/{created_instruction.id}", headers=headers)
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=2, instruction_id=1, user=unittest.mock.ANY)

    def test_delete_instruction_with_non_existing_instruction_fail(
        self, use_test_db, mocker, bypass_published_filter, user
    ):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        headers = {"Authorization": "Bearer token"}
        response = self.client.delete(f"/api/recipes/{created_recipe.id}/instructions/{2}", headers=headers)
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=2, user=unittest.mock.ANY)

    def test_delete_instruction_with_wrong_recipe_fail(self, use_test_db, mocker, bypass_published_filter, user):
        operations.create_category("Category", 1)
        operations.create_recipe(**self.recipe)
        operations.create_recipe(**self.recipe)
        operations.create_instruction(
            recipe_id=1, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )
        operations.create_instruction(
            recipe_id=2, instruction_request=CreateInstructionInputModel(**self.new_instruction), user=user
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        headers = {"Authorization": "Bearer token"}
        response = self.client.delete(f"/api/recipes/{1}/instructions/{2}", headers=headers)
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=2, user=unittest.mock.ANY)
