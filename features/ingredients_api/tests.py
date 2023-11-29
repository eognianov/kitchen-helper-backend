import pytest
import db.connection
from tests.fixtures import use_test_db
from features.ingredients_api import operations
from features.ingredients_api.models import Ingredient, IngredientCategory
from features.ingredients_api.exceptions import (
    IngredientNameViolationException,
    IngredientNotFoundException,
    IngredientCategoryNameViolation,
    IngredientCategoryNotFoundException,
)
from fastapi.testclient import TestClient
from api import app


class TestIngredientCategoryOperations:
    def test_create_ingredient_category_operation(self, use_test_db, mocker):
        expected_name = "new_category"
        operations.create_ingredient_category(expected_name)

        with db.connection.get_session() as session:
            categories = session.query(IngredientCategory).all()

        assert len(categories) == 1
        assert categories[0].name == expected_name


def test_create_ingredient_category_with_existing_name(self, use_test_db):
    expected_name = "new_category"
    operations.create_ingredient_category(expected_name)

    with pytest.raises(IngredientCategoryNameViolation):
        operations.create_ingredient_category(expected_name)


def test_get_category_by_id_success(self, use_test_db):
    created_category = operations.create_ingredient_category("name")
    category_from_db = operations.get_ingredient_category_by_id(created_category.id)

    assert created_category.name == category_from_db.name
    assert created_category.created_by == category_from_db.created_by
    assert created_category.created_on == category_from_db.created_on


def test_get_category_by_id_not_fail(self, use_test_db):
    with pytest.raises(IngredientCategoryNotFoundException):
        operations.get_ingredient_category_by_id(1)


def test_get_all_categories(self, use_test_db):
    assert len(operations.get_all_ingredients_category()) == 0
    operations.create_ingredient_category("new")
    assert len(operations.get_all_ingredients_category()) == 1


def test_update_category(self, use_test_db):
    created_category = operations.create_ingredient_category("name")
    operations.update_ingredient_category(created_category.id, "name", "new_name")
    updated_category = operations.get_ingredient_category_by_id(created_category.id)
    assert updated_category.name == "new_name"


class TestIngredientOperations:
    def test_create_ingredient_operation(self, use_test_db, mocker):
        expected_name = "new_ingredient"
        operations.create_ingredient(expected_name)

        with db.connection.get_session() as session:
            ingredients = session.query(Ingredient).all()

        assert len(ingredients) == 1
        assert ingredients[0].name == expected_name

    def test_create_ingredient_with_existing_name(self, use_test_db):
        expected_name = "new_category"
        operations.create_ingredient(expected_name)

        with pytest.raises(IngredientNameViolationException):
            operations.create_ingredient(expected_name)

    def test_get_ingredient_by_id_success(self, use_test_db):
        created_ingredient = operations.create_ingredient("name")
        ingredient_from_db = operations.get_ingredient(created_ingredient.id)

        assert created_ingredient.name == ingredient_from_db.name
        assert created_ingredient.created_by == ingredient_from_db.created_by
        assert created_ingredient.created_on == ingredient_from_db.created_on

    def test_get_ingredient_by_id_not_fail(self, use_test_db):
        with pytest.raises(IngredientNotFoundException):
            operations.get_ingredient(1)

    def test_get_all_ingredients(self, use_test_db):
        assert len(operations.get_all_ingredients()) == 0
        operations.create_ingredient("new")
        assert len(operations.get_all_ingredients()) == 1

    def test_update_ingredient(self, use_test_db):
        created_ingredient = operations.create_ingredient("name")
        operations.update_ingredient(created_ingredient.id, "name", "new_name")
        updated_ingredient = operations.get_ingredient(created_ingredient.id)
        assert updated_ingredient.name == "new_name"


class TestIngredientsEndpoints:
    client = TestClient(app)

    @classmethod
    def test_get_all_ingredients_empty(cls, use_test_db, mocker):
        get_all_ingredients_spy = mocker.spy(operations, "get_all_ingredients")
        response = cls.client.get("/ingredients/")
        assert response.status_code == 200
        assert get_all_ingredients_spy.call_count == 1

    @classmethod
    def test_get_all_ingredients(cls, use_test_db, mocker):
        created_ingredient = operations.create_ingredient("new")
        get_all_ingredients_spy = mocker.spy(operations, "get_all_ingredients")
        response = cls.client.get("/ingredients/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert get_all_ingredients_spy.call_count == 1

    @classmethod
    def test_get_ingredient_by_id(cls, use_test_db, mocker):
        created_ingredient = operations.create_ingredient("new")
        get_ingredient_spy = mocker.spy(operations, "get_ingredient_by_id")
        response = cls.client.get(f"/ingredients/{created_ingredient.id}")
        assert response.status_code == 200
        get_ingredient_spy.assert_called_with(created_ingredient.id)

    @classmethod
    def test_patch_ingredient(cls, use_test_db, mocker):
        created_ingredient = operations.create_ingredient("new")
        patch_payload = {"field": "name", "value": "updated"}
        update_ingredient_spy = mocker.spy(operations, "update_ingredient")
        response = cls.client.patch(
            f"/ingredients/{created_ingredient.id}", json=patch_payload
        )
        assert response.status_code == 200
        update_ingredient_spy.assert_called_with(
            ingredient_id=1, field="name", value="updated"
        )
