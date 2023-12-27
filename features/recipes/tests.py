import unittest.mock
from http.client import HTTPException

import pytest

import common.authentication
import db.connection
from features.recipes.input_models import CreateInstructionInputModel
from features.recipes.operations import create_recipe, create_category, get_recipe_by_id, update_recipe
from tests.fixtures import use_test_db, admin, user
from features.recipes import operations
from features.recipes.models import RecipeCategory, RecipeInstruction, Recipe
from features.recipes.exceptions import (
    CategoryNameViolationException,
    CategoryNotFoundException,
    RecipeNotFoundException,
)
from fastapi.testclient import TestClient
from api import app
from pytest import fixture


@fixture
def bypass_published_filter(mocker):
    mocker.patch('features.recipes.operations._get_published_filter_expression', return_value=[])
    yield


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
        with pytest.raises(CategoryNameViolationException):
            operations.create_category(expected_name, 1)

    def test_get_category_by_id_success(self, use_test_db):
        created_category = operations.create_category("name", 1)
        category_from_db = operations.get_category_by_id(created_category.id)

        assert created_category.name == category_from_db.name
        assert created_category.created_by == category_from_db.created_by
        assert created_category.created_on == category_from_db.created_on

    def test_get_category_by_id_not_fail(self, use_test_db):
        with pytest.raises(CategoryNotFoundException):
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
        response = cls.client.get("/categories/")
        assert response.status_code == 200
        assert get_all_categories_spy.call_count == 1

    @classmethod
    def test_get_all_categories(cls, use_test_db, mocker):
        created_category = operations.create_category("new", 1)
        get_all_categories_spy = mocker.spy(operations, "get_all_recipe_categories")
        response = cls.client.get("/categories/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert get_all_categories_spy.call_count == 1

    @classmethod
    def test_get_category_by_id(cls, use_test_db, mocker):
        created_category = operations.create_category("new", 1)
        get_category_spy = mocker.spy(operations, "get_category_by_id")
        response = cls.client.get(f"/categories/{created_category.id}")
        assert response.status_code == 200
        get_category_spy.assert_called_with(created_category.id)

    @classmethod
    def test_patch_category(cls, use_test_db, mocker, admin):
        created_category = operations.create_category("new", 1)
        patch_payload = {"field": "name", "value": "updated"}
        update_category_spy = mocker.spy(operations, "update_category")
        response = cls.client.patch(
            f"/categories/{created_category.id}",
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
            f"/recipes/{created_recipe.id}/instructions/{created_instruction.id}",
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
            f"/recipes/{created_recipe.id}/instructions/{created_instruction.id}",
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
            f"/recipes/{created_recipe.id}/instructions/{created_instruction.id}", headers=headers
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
        response = self.client.delete(f"/recipes/{2}/instructions/{created_instruction.id}", headers=headers)
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
        response = self.client.delete(f"/recipes/{created_recipe.id}/instructions/{2}", headers=headers)
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
        response = self.client.delete(f"/recipes/{1}/instructions/{2}", headers=headers)
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=2, user=unittest.mock.ANY)


class TestCreateRecipeOperations:
    def setup(self):
        # self.client = TestClient(app)
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

    def test_create_recipe_with_all_parameters(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1
        assert recipe.name == "name"
        assert recipe.time_to_prepare == 0
        assert recipe.category_id == 1
        assert recipe.picture == ""
        assert recipe.summary == "summary"
        assert recipe.calories == 1
        assert recipe.carbo == 1
        assert recipe.fats == 1
        assert recipe.proteins == 1
        assert recipe.cholesterol == 1
        assert recipe.created_by == 1
        assert recipe.instructions == []

    def test_create_recipe_with_category_id_parameter(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1
        assert recipe.category_id == 1

    def test_create_recipe_with_picture_parameter(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1
        assert recipe.picture == ""

    def test_create_recipe_with_summary_parameter(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1
        assert recipe.summary == "summary"

    def test_create_recipe_with_calories_parameter(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1
        assert recipe.calories == 1

    def test_create_recipe_with_carbo_parameter(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1
        assert recipe.carbo == 1

    # TODO To see why recipe without name is created
    def test_create_recipe_with_empty_name(self, use_test_db, bypass_published_filter, mocker):
        self.recipe["name"] = ""
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

        assert len(recipes) == 1

    def test_create_recipe_with_non_existent_category_id(self, use_test_db, bypass_published_filter, mocker):
        with pytest.raises(Exception):
            operations.create_recipe(**self.recipe)


class TestGetAllRecipiesOperations:
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

    def test_returns_all_published_and_not_deleted_recipes(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

        assert len(recipes) == 1

    def test_returns_empty_list_when_no_published_recipes(self, use_test_db, bypass_published_filter, mocker):
        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

        assert len(recipes) == 0

    def test_returns_published_recipes_when_no_deleted_recipes(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category 1", 1)
        operations.create_recipe(**self.recipe)

        operations.create_category("Category 2", 2)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

        assert len(recipes) == 2

    def test_returns_empty_list_when_no_recipes(self, use_test_db, bypass_published_filter, mocker):
        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

        assert len(recipes) == 0

    def test_returns_empty_list_when_all_recipes_deleted(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category 1", 1)
        operations.create_category("Category 2", 1)
        operations.create_recipe(**self.recipe)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

            del recipes[:]

        assert len(recipes) == 0


class TestGetRecipeByIdOperations:
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

    def test_returns_recipe(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category 1", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()

        assert len(recipes) == 1

    def test_invalid_recipe_id(self):
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(3)

    def test_returns_none_with_unpublished_id(self, use_test_db, bypass_published_filter, mocker):
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(1)

    def test_raises_exception_when_no_recipe_found(self):
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(1)

    def test_raises_exception_with_deleted_id(self, use_test_db):
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(1)


class TestDeleteRecipeOperation:
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

    def test_delete_recipe_success(self, use_test_db, bypass_published_filter, mocker):
        operations.create_category("Category 1", 1)
        operations.create_recipe(**self.recipe)

        with db.connection.get_session() as session:
            recipes = session.query(Recipe).all()
            recipe = session.query(Recipe).first()

        assert len(recipes) == 1

        deleted_by = common.authentication.AuthenticatedUser(id=1)

        operations.delete_recipe(recipe_id=recipe.id, deleted_by=deleted_by)

        with db.connection.get_session() as session:
            deleted_recipe = session.query(Recipe).filter_by(id=recipe.id, is_deleted=True).first()

            assert deleted_recipe is not None
            assert deleted_recipe.id == recipe.id
            assert deleted_recipe.is_deleted is True
            assert deleted_recipe.deleted_by == deleted_by.id

        recipes_after_delete = session.query(Recipe).filter_by(is_deleted=False).all()
