import unittest.mock

import pytest

import common.authentication
import db.connection
from features.recipes.input_models import CreateInstructionInputModel
from features.recipes.operations import create_recipe, create_category
from tests.fixtures import use_test_db, admin, user
from features.recipes import operations
from features.recipes.models import RecipeCategory, RecipeInstruction, Recipe
from features.recipes.exceptions import (
    CategoryNameViolationException,
    CategoryNotFoundException,
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
        operations.create_recipe(**self.recipe)
        operations.create_category("Category name", 1)

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

class TestCreateRecipesOperations:

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

    def test_create_recipe_with_all_parameters(self, use_test_db, mocker):

        operations.create_recipe(**self.recipe)
        operations.create_category("Category name", )

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

    def test_create_recipe_with_all_parameters(self, mocker):

        # mocker.patch('db.connection.get_session')

        category = create_category("Test Category")

        # TODO here must be create a user and like that I will can make a valid category

        print(category)

        result = create_recipe(
            name="Test Recipe",
            time_to_prepare=30,
            category_id=category.id,
            picture="test.jpg",
            summary="This is a test recipe",
            calories=100,
            carbo=10,
            fats=5,
            proteins=20,
            cholesterol=0.5,
            created_by="me"
        )

        assert result.name == "Test Recipe"
        assert result.time_to_prepare == 30
        assert result.category_id == 1
        assert result.picture == "test.jpg"
        assert result.summary == "This is a test recipe"
        assert result.calories == 100
        assert result.carbo == 10
        assert result.fats == 5
        assert result.proteins == 20
        assert result.cholesterol == 0.5
        assert result.created_by == "me"

    def test_create_recipe_with_category_id_parameter(self):

        category = RecipeCategory(name="Test Category")

        # TODO Is it that possible to create a recipe category without user in created_by or not?

        with patch("db.connection.get_session") as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.where.return_value.first.return_value = category
            recipe = create_recipe(name="Test Recipe", time_to_prepare=30, category_id=1)

            assert recipe.category.id == 1

    def test_create_recipe_with_picture_parameter(self):

        recipe = create_recipe(name="Test Recipe", time_to_prepare=30, picture="test.jpg")
        assert recipe.picture == "test.jpg"

        #     TODO I need to create a fake user

    def test_create_recipe_with_summary_parameter(self):

        recipe = create_recipe(name="Test Recipe", time_to_prepare=30, summary="This is a test recipe")
        assert recipe.summary == "This is a test recipe"

        #     TODO I need to create a fake user


    def test_create_recipe_with_calories_parameter(self):

        recipe = create_recipe(name="Test Recipe", time_to_prepare=30, calories=100)
        assert recipe.calories == 100

        #     TODO I need to create a fake user


    def test_create_recipe_with_carbo_parameter(self):

        recipe = create_recipe(name="Test Recipe", time_to_prepare=30, carbo=10.5)

        assert recipe.name == "Test Recipe"
        assert recipe.time_to_prepare == 30
        assert recipe.carbo == 10.5

        #     TODO I need to create a fake user


    def test_create_recipe_with_empty_name(self, mocker):

        mocker.patch('db.connection.get_session')

        with pytest.raises(ValueError):
            create_recipe(name="", time_to_prepare=30)

            #     TODO I need to create a fake user

    def test_create_recipe_with_non_existent_category_id(self, mocker):

        mocker.patch('db.connection.get_session')

        with pytest.raises(CategoryNotFoundException):
            create_recipe(name="Test Recipe", time_to_prepare=30, category_id=1)

            #     TODO I need to create a fake user


class TestGetAllRecipiesOperations:

    @pytest.fixture
    def mock_session(self, mocker):
        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

        # Mock the enter function
        enter_mock = mocker.MagicMock()
        enter_mock.return_value = session_mock

        # Mock the querry function
        query_mock = mocker.MagicMock()
        session_mock.query.return_value = query_mock

        # Mock the join function
        join_mock = mocker.MagicMock()
        query_mock.join.return_value = join_mock

        # Mock the filter function
        filter_mock = mocker.MagicMock()
        join_mock.filter.return_value = filter_mock

        # Mock the all function
        all_mock = mocker.MagicMock()
        filter_mock.all.return_value = all_mock

        return all_mock, session_mock, query_mock, join_mock, filter_mock, enter_mock

    def test_returns_all_published_and_not_deleted_recipes(self, mocker, mock_session):

        all_mock, session_mock, query_mock, join_mock, filter_mock = mock_session

        result = get_all_recipes()

        # Assertions

        assert result == all_mock
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_no_published_recipes(self, mocker, mock_session):
        session_mock, query_mock, join_mock, filter_mock = mock_session

        mocker.patch('db.connection.get_session')

        result = get_all_recipes()

        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_published_recipes_when_no_deleted_recipes(self, mocker, mock_session):

        session_mock, query_mock, join_mock, filter_mock, all_mock = mock_session

        mocker.patch('db.connection.get_session')

        result = get_all_recipes()

        # Assertions
        assert result == all_mock
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_no_recipes(self, mocker, mock_session):

        session_mock, query_mock, join_mock, filter_mock = mock_session

        mocker.patch('db.connection.get_session')

        result = get_all_recipes()

        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_all_recipes_deleted(self, mocker, mock_session):

        session_mock, query_mock, join_mock, filter_mock = mock_session

        mocker.patch('db.connection.get_session')

        result = get_all_recipes()

        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_all_recipes_not_published(self, mocker, mock_session):

        session_mock, query_mock, join_mock, filter_mock = mock_session

        mocker.patch('db.connection.get_session')

        result = get_all_recipes()

        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

class TestGetRecipeByIdOperations:

    def test_returns_recipe(self):

        result = get_recipe_by_id(1)

        assert isinstance(result, Recipe)

    def test_invalid_recipe_id(self):

        result = get_recipe_by_id(-1)

        assert result is None

    def test_returns_none_with_deleted_id(self, mocker):

        recipe_id = 1

        recipe = Recipe(id=recipe_id, name="Test Recipe", time_to_prepare=30, created_by=1,
                        created_on=datetime.utcnow(), updated_by=None,updated_on=None,
                        category=None, category_id=None, picture=None,
                        summary=None, calories=None, carbo=None,
                        fats=None, proteins=None, cholesterol=None,
                        is_published=True, published_on=datetime.utcnow(),
                        published_by=1, is_deleted=True,
                        deleted_on=datetime.utcnow(), deleted_by=1)

        mocker.patch('db.connection.get_session')
        session_mock = db.connection.get_session.return_value.__enter__.return_value
        session_mock.query.return_value.\
            join.return_value.where.return_value.filter.\
            return_value.one_or_none.return_value = recipe

        result = get_recipe_by_id(recipe_id)

        assert result is None

    def test_returns_none_with_unpublished_id(self, mocker):

        recipe = Recipe(id=1, name="Test Recipe",
                        time_to_prepare=30, created_by=1,
                        created_on=datetime.utcnow(),
                        updated_by=None, updated_on=None,
                        category=None, category_id=None,
                        picture=None, summary=None,
                        calories=None, carbo=None,
                        fats=None, proteins=None,
                        cholesterol=None, is_published=False,
                        published_on=None, published_by=None,
                        is_deleted=False, deleted_on=None,
                        deleted_by=None)

        mocker.patch('db.connection.get_session')
        session_mock = db.connection.get_session.return_value.__enter__.return_value
        session_mock.query.return_value.join.return_value.where.return_value.filter.return_value.one_or_none.return_value = recipe

        result = get_recipe_by_id(1)

        assert result is None

    def test_raises_exception_when_no_recipe_found(self, mocker):

        recipe_id = 1
        mocker.patch('db.connection.get_session')
        session_mock = db.connection.get_session.return_value.__enter__.return_value
        session_mock.query.return_value.join.return_value.where.return_value.filter.return_value.one_or_none.return_value = None

        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(recipe_id)

    def test_raises_exception_with_deleted_id(self, mocker):

        recipe = Recipe(id=1, name="Test Recipe",
                        time_to_prepare=30, created_by=1,
                        created_on=datetime.utcnow(),
                        updated_by=None, updated_on=None,
                        category=None, category_id=None,
                        picture=None, summary=None,
                        calories=None, carbo=None,
                        fats=None, proteins=None,
                        cholesterol=None, is_published=True,
                        published_on=datetime.utcnow(),
                        published_by=1, is_deleted=True,
                        deleted_on=datetime.utcnow(),
                        deleted_by=1)

        mocker.patch('db.connection.get_session')
        session_mock = db.connection.get_session.return_value.__enter__.return_value
        session_mock.query.return_value.join.return_value.where.return_value.filter.return_value.one_or_none.return_value = recipe

        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(1)

    def test_raises_exception_with_unpublished_id(self, mocker):

        recipe = Recipe(id=1, name="Test Recipe",
                        time_to_prepare=30, created_by=1,
                        created_on=datetime.utcnow(),
                        updated_by=None, updated_on=None,
                        category=None, category_id=None,
                        picture=None, summary=None,
                        calories=None, carbo=None,
                        fats=None, proteins=None,
                        cholesterol=None, is_published=False,
                        published_on=None, published_by=None,
                        is_deleted=False, deleted_on=None,
                        deleted_by=None)

        mocker.patch('db.connection.get_session')
        session_mock = db.connection.get_session.return_value.__enter__.return_value
        session_mock.query.return_value.join.return_value.where.return_value.filter.return_value.one_or_none.return_value = recipe

        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(1)

    def test_returns_none_with_non_integer_id(self, mocker):

        mocker.patch("db.connection.get_session")

        result = get_recipe_by_id("1")

        assert result is None

class TestUpdateRecipeOperation:

    def test_update_specified_field(self):

        recipe_id = 1
        field = "name"
        value = "New Recipe Name"
        updated_by = "User1"

        updated_recipe = update_recipe(recipe_id, field, value, updated_by)

        self.assertEqual(updated_recipe.name, value)
        self.assertEqual(updated_recipe.updated_by, updated_by)

    def test_update_recipe_raises_http_exception_if_recipe_not_found(self):

        with self.assertRaises(HTTPException) as context:
            update_recipe(recipe_id=1, field="name",
                          value="New Recipe Name", updated_by="John Die")

        self.assertEqual(context.exception.status_code, 404)

class TestDeleteRecipeOperation:

    def test_delete_recipe_success(self):

        recipe_id = 1
        deleted_by = 1

        recipe = Recipe(id=recipe_id, is_deleted=False, is_published= True)

        mocker.patch("path.to.get_recipe_by_id", return_value=recipe)
        session_mock = mocker.MagicMock()
        session_mock.execute.return_value = None
        session_mock.commit.return_value = None
        mocker.patch("path.to.db.connection.get_session", return_value=session_mock)

        result = delete_recipe(recipe_id=recipe_id, deleted_by=deleted_by)

        assert result == recipe

        session_mock.execute.assert_called_with(
            update(Recipe),
            [
                {
                    "id": recipe.id,
                    "is_deleted": True,
                    "deleted_on": datetime.utcnow(),
                    "deleted_by": deleted_by
                }
            ],
        )
        session_mock.commit.assert_called_once()

    def test_delete_recipe_marks_as_deleted(self):

        recipe_id = 1
        deleted_by = 1

        recipe = Recipe(id=recipe_id, is_deleted=False, is_published=True)

        mocker.patch("path.to.get_recipe_by_id", return_value=recipe)
        session_mock = mocker.MagicMock()
        session_mock.execute.return_value = None
        session_mock.commit.return_value = None
        mocker.patch("path.to.db.connection.get_session", return_value=session_mock)

        delete_recipe(recipe_id=recipe_id, deleted_by=deleted_by)

        assert recipe.is_deleted is True

    def test_delete_recipe_raise_exception_if_recipe_not_found(self):

        mocker.patch("path.to.get_recipe_by_id", side_effect=RecipeNotFoundException)

        with self.assertRaises(Exception):
            delete_recipe(recipe_id=1, deleted_by=1)

    def test_exception_no_modification(self):

        with patch('module.get_recipe_by_id', side_effect=RecipeNotFoundException):

            with patch('module.session') as mock_session:

                with self.assertRaises(RecipeNotFoundException):
                    delete_recipe(recipe_id=1, deleted_by=1)

                mock_session.execute.assert_not_called()

                mock_session.commit.assert_not_called()