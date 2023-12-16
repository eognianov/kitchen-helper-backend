import pytest

import common.authentication
import db.connection
from features.recipes.input_models import CreateInstructionInputModel
from tests.fixtures import use_test_db, admin
from features.recipes import operations
from features.recipes.models import RecipeCategory, RecipeInstruction, Recipe
from features.recipes.exceptions import (
    CategoryNameViolationException,
    CategoryNotFoundException,
)
from fastapi.testclient import TestClient
from api import app


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
        update_category_spy.assert_called_with(
            category_id=1, field="name", value="updated", updated_by=1
        )


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

    def test_create_recipe_with_instructions_success(self, use_test_db):
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

    def test_create_instruction_for_recipe_success(self, use_test_db):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**new_instruction),
        )

        with db.connection.get_session() as session:
            instructions = session.query(RecipeInstruction).all()
            instruction = session.query(RecipeInstruction).first()
            assert len(instructions) == 1
            assert instruction.instruction == new_instruction["instruction"]
            assert instruction.category == new_instruction["category"].capitalize()
            assert instruction.time == new_instruction["time"]
            assert instruction.complexity == new_instruction["complexity"]

    def test_get_instruction_by_id_success(self, use_test_db):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**new_instruction),
        )

        instruction = operations.get_instruction_by_id(instruction_id=1)
        assert instruction.instruction == new_instruction["instruction"]
        assert instruction.category == new_instruction["category"].capitalize()
        assert instruction.time == new_instruction["time"]
        assert instruction.complexity == new_instruction["complexity"]

    def test_update_instruction_success(self, use_test_db):
        operations.create_category("Category name", 1)
        operations.create_recipe(**self.recipe)

        new_instruction = {
            "instruction": "instruction",
            "category": "lunch",
            "time": 10,
            "complexity": 5,
        }

        created_instruction = operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**new_instruction),
        )
        operations.update_instruction(
            recipe_id=1,
            instruction_id=created_instruction.id,
            field="instruction",
            value="new_name",
        )
        operations.update_instruction(
            recipe_id=1,
            instruction_id=created_instruction.id,
            field="category",
            value="Breakfast",
        )
        operations.update_instruction(
            recipe_id=1, instruction_id=created_instruction.id, field="time", value="20"
        )
        operations.update_instruction(
            recipe_id=1,
            instruction_id=created_instruction.id,
            field="complexity",
            value="1",
        )
        updated_instruction = operations.get_instruction_by_id(created_instruction.id)
        assert updated_instruction.instruction == "new_name"
        assert updated_instruction.category == "Breakfast"
        assert updated_instruction.time == 20
        assert updated_instruction.complexity == 1

    def test_delete_instruction_success(self, use_test_db):
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
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**new_instruction),
        )
        operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**new_instruction2),
        )

        operations.delete_instruction(recipe_id=1, instruction_id=2)

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

    def test_patch_instruction_success(self, use_test_db, mocker):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )

        patch_payload = {"field": "instruction", "value": "updated"}

        update_instruction_spy = mocker.spy(operations, "update_instruction")
        response = self.client.patch(
            f"/recipes/{created_recipe.id}/instructions/{created_instruction.id}",
            json=patch_payload,
        )
        assert response.status_code == 200
        update_instruction_spy.assert_called_with(
            recipe_id=1, instruction_id=1, field="instruction", value="updated"
        )

    def test_patch_instruction_with_wrong_field_fail(self, use_test_db, mocker):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )

        patch_payload = {"field": "test", "value": "updated"}

        response = self.client.patch(
            f"/recipes/{created_recipe.id}/instructions/{created_instruction.id}",
            json=patch_payload,
        )
        assert response.status_code == 422

    def test_delete_instruction_success(self, use_test_db, mocker):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        response = self.client.delete(
            f"/recipes/{created_recipe.id}/instructions/{created_instruction.id}"
        )
        assert response.status_code == 204
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=1)

    def test_delete_instruction_with_non_existing_recipe_fail(
        self, use_test_db, mocker
    ):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        response = self.client.delete(
            f"/recipes/{2}/instructions/{created_instruction.id}"
        )
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=2, instruction_id=1)

    def test_delete_instruction_with_non_existing_instruction_fail(
        self, use_test_db, mocker
    ):
        operations.create_category("Category", 1)
        created_recipe = operations.create_recipe(**self.recipe)
        created_instruction = operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        response = self.client.delete(f"/recipes/{created_recipe.id}/instructions/{2}")
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=2)

    def test_delete_instruction_with_wrong_recipe_fail(self, use_test_db, mocker):
        operations.create_category("Category", 1)
        operations.create_recipe(**self.recipe)
        operations.create_recipe(**self.recipe)
        operations.create_instruction(
            recipe_id=1,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )
        operations.create_instruction(
            recipe_id=2,
            instruction_request=CreateInstructionInputModel(**self.new_instruction),
        )

        delete_instruction_spy = mocker.spy(operations, "delete_instruction")
        response = self.client.delete(f"/recipes/{1}/instructions/{2}")
        assert response.status_code == 404
        delete_instruction_spy.assert_called_with(recipe_id=1, instruction_id=2)
