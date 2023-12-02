import pytest
import db.connection
from tests.fixtures import use_test_db
from features.recipes import operations
from features.recipes.models import RecipeCategory
from features.recipes.exceptions import CategoryNameViolationException, CategoryNotFoundException
from fastapi.testclient import TestClient
from api import app


class TestCategoryOperations:
    def test_create_category_success(self, use_test_db, mocker):
        expected_name = 'new_category'
        operations.create_category(expected_name)
        with db.connection.get_session() as session:
            categories = session.query(RecipeCategory).all()
        assert len(categories) == 1
        assert categories[0].name == expected_name

    def test_create_category_with_existing_name(self, use_test_db):
        expected_name = 'new_category'
        operations.create_category(expected_name)
        with pytest.raises(CategoryNameViolationException):
            operations.create_category(expected_name)

    def test_get_category_by_id_success(self, use_test_db):
        created_category = operations.create_category('name')
        category_from_db = operations.get_category_by_id(created_category.id)

        assert created_category.name == category_from_db.name
        assert created_category.created_by == category_from_db.created_by
        assert created_category.created_on == category_from_db.created_on

    def test_get_category_by_id_not_fail(self, use_test_db):
        with pytest.raises(CategoryNotFoundException):
            operations.get_category_by_id(1)

    def test_get_all_categories(self, use_test_db):
        assert len(operations.get_all_recipe_categories()) == 0
        operations.create_category('new')
        assert len(operations.get_all_recipe_categories()) == 1

    def test_update_category(self, use_test_db):
        created_category = operations.create_category('name')
        operations.update_category(created_category.id, 'name', 'new_name')
        updated_category = operations.get_category_by_id(created_category.id)
        assert updated_category.name == 'new_name'


class TestCategoriesEndpoints:
    client = TestClient(app)

    @classmethod
    def test_get_all_categories_empty(cls, use_test_db, mocker):
        get_all_categories_spy = mocker.spy(operations, 'get_all_recipe_categories')
        response = cls.client.get('/categories/')
        assert response.status_code == 200
        assert get_all_categories_spy.call_count == 1

    @classmethod
    def test_get_all_categories(cls, use_test_db, mocker):
        created_category = operations.create_category('new')
        get_all_categories_spy = mocker.spy(operations, 'get_all_recipe_categories')
        response = cls.client.get('/categories/')
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert get_all_categories_spy.call_count == 1

    @classmethod
    def test_get_category_by_id(cls, use_test_db, mocker):
        created_category = operations.create_category('new')
        get_category_spy = mocker.spy(operations, 'get_category_by_id')
        response = cls.client.get(f'/categories/{created_category.id}')
        assert response.status_code == 200
        get_category_spy.assert_called_with(created_category.id)

    @classmethod
    def test_patch_category(cls, use_test_db, mocker):
        created_category = operations.create_category('new')
        patch_payload = {
            'field': 'name',
            'value': 'updated'
        }
        update_category_spy = mocker.spy(operations, 'update_category')
        response = cls.client.patch(f'/categories/{created_category.id}', json=patch_payload)
        assert response.status_code == 200
        update_category_spy.assert_called_with(
            category_id=1, field="name", value="updated"
        )

class TestCreateRecipesOperations:

    def test_create_recipe_with_mandatory_parameters(self, mocker):

        """Creates a recipe with mandatory parameters"""
        """Happy path test"""

        # Mock the get_category_by_id function
        mocker.patch('db.connection.get_session')
        mocker.patch('db.connection.get_session().__enter__')
        mocker.patch('db.connection.get_session().__exit__')
        mocker.patch('db.connection.get_session().__enter__.return_value.query')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where.return_value.first')

        # Call the create_recipe function with mandatory parameters
        result = create_recipe(name="Test Recipe", time_to_prepare=30)

        # Assert that the recipe is created with the correct name and time_to_prepare

        assert result.name == "Test Recipe"
        assert result.time_to_prepare == 30
        assert result.category is None
        assert result.picture is None
        assert result.summary is None
        assert result.calories == 0
        assert result.carbo == 0
        assert result.fats == 0
        assert result.proteins == 0
        assert result.cholesterol == 0
        assert result.created_by == "me"

    def test_create_recipe_with_all_parameters(self, mocker):

        """Creates a recipe with all parameters"""
        """Happy path test"""

        # Mock the get_category_by_id function
        mocker.patch('db.connection.get_session')
        mocker.patch('db.connection.get_session().__enter__')
        mocker.patch('db.connection.get_session().__exit__')
        mocker.patch('db.connection.get_session().__enter__.return_value.query')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where.return_value.first')

        # Call the create_recipe function with all parameters
        result = create_recipe(
            name="Test Recipe",
            time_to_prepare=30,
            category_id=1,
            picture="test.jpg",
            summary="This is a test recipe",
            calories=100,
            carbo=10,
            fats=5,
            proteins=20,
            cholesterol=0.5,
            created_by="me"
        )

        # Assert that the recipe is created with the correct values
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

        """Creates a recipe with category_id is parameter"""
        """Happy path test"""

        category_id = 1
        category = RecipeCategory(id=category_id, name="Test Category")

        with patch("db.connection.get_session") as mock_session:
            mock_session.return_value.__enter__.return_value.query.return_value.where.return_value.first.return_value = category
            recipe = create_recipe(name="Test Recipe", time_to_prepare=30, category_id=category_id)

            assert recipe.category.id == category_id

    def test_create_recipe_with_picture_parameter(self):

        """Creates a recipe with picture parameter"""
        """Happy path test"""

        recipe_name = "Test Recipe"
        recipe_time_to_prepare = 30
        recipe_picture = "test.jpg"

        recipe = create_recipe(name=recipe_name, time_to_prepare=recipe_time_to_prepare, picture=recipe_picture)
        assert recipe.picture == "test.jpg"

    def test_create_recipe_with_summary_parameter(self):

        """Creates a recipe with summary parameter"""
        """Happy path test"""

        recipe_name = "Test Recipe"
        recipe_time_to_prepare = 30

        recipe = create_recipe(name=recipe_name, time_to_prepare=recipe_time_to_prepare, summary="This is a test recipe")
        assert recipe.summary == "This is a test recipe"

    def test_create_recipe_with_calories_parameter(self):

        """Creates a recipe with calories parameter"""
        """Happy path test"""

        recipe = create_recipe(name="Test Recipe", time_to_prepare=30, calories=100)
        assert recipe.calories == 100

    def test_create_recipe_with_carbo_parameter(self):

        """Creates a recipe with carbo parameter"""
        """Happy path test"""

        # Arrange
        name = "Test Recipe"
        time_to_prepare = 30
        carbo = 10.5

        # Act
        recipe = create_recipe(name=name, time_to_prepare=time_to_prepare, carbo=carbo)

        # Assert
        assert recipe.name == name
        assert recipe.time_to_prepare == time_to_prepare
        assert recipe.carbo == carbo

    def test_create_recipe_with_empty_name(self, mocker):

        """Creates a recipe with summary parameter"""
        """Edge case test"""

        # Mock the get_category_by_id function
        mocker.patch('db.connection.get_session')
        mocker.patch('db.connection.get_session().__enter__')
        mocker.patch('db.connection.get_session().__exit__')
        mocker.patch('db.connection.get_session().__enter__.return_value.query')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where.return_value.first')

        # Assert that ValueError is when creating a recipe with an empty name
        with pytest.raises(ValueError):
            create_recipe(name="", time_to_prepare=30)

    @classmethod
    def test_create_recipe_with_non_existent_category_id(self, mocker):

        """Creates a recipe with non-existent category_id raises CategoryNotFoundException"""
        """Edge case test"""

        # Mock the get_category_by_id function to raise CategoryNotFoundException
        mocker.patch('db.connection.get_session')
        mocker.patch('db.connection.get_session().__enter__')
        mocker.patch('db.connection.get_session().__exit__')
        mocker.patch('db.connection.get_session().__enter__.return_value.query')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where')
        mocker.patch('db.connection.get_session().__enter__.return_value.query.return_value.where.return_value.first')
        mocker.patch('exceptions.CategoryNotFoundException')

        # Call the create_recipe function with non-existent category_id
        with pytest.raises(CategoryNotFoundException):
            create_recipe(name="Test Recipe", time_to_prepare=30, category_id=1)

class TestGetAllRecipiesOperations:


    def test_returns_all_published_and_not_deleted_recipes(self, mocker):

        """Returns all published and not deleted recipes"""
        """Happy path test"""

        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

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

        # Call the function under test
        result = get_all_recipes()

        # Assertions

        assert result == all_mock
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_no_published_recipes(self, mocker):

        """Returns empty list when no published recipes"""
        """Happy path test"""

        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

        # Mock the query function
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

        # Call the function under test
        result = get_all_recipes()

        # Assertions
        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_published_recipes_when_no_deleted_recipes(self, mocker):

        """Returns empty list when no recipes"""
        """Happy path test"""

        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

        # Mock the query function
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

        # Call the function under test
        result = get_all_recipes()

        # Assertions
        assert result == all_mock
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_no_recipes(self, mocker):

        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

        # Mock the query function
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

        # Call the function under test
        result = get_all_recipes()

        # Assertions
        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_all_recipes_deleted(self, mocker):

        """Returns empty list when all recipes deleted"""
        """Happy path test"""

        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

        # Mock the query function
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

        # Call the function under test
        result = get_all_recipes()

        # Assertions
        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

    def test_returns_empty_list_when_all_recipes_not_published(self, mocker):
        # Mock the get_session function
        mocker.patch('db.connection.get_session')
        session_mock = mocker.MagicMock()
        db.connection.get_session.return_value = session_mock

        # Mock the query function
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

        # Call the function under test
        result = get_all_recipes()

        # Assertions
        assert result == []
        session_mock.query.assert_called_once_with(Recipe)
        query_mock.join.assert_called_once_with(Recipe.category, isouter=True)
        join_mock.filter.assert_called_once_with(and_(Recipe.is_deleted.is_(False), Recipe.is_published.is_(True)))
        filter_mock.all.assert_called_once_with()

class TestGetRecipeByIdOperations:

    def test_returns_recipe(self):

        """Returns a recipe object when given a valid recipe id"""
        """Happy path test"""

        # Arrange
        recipe_id = 1

        # Act
        result = get_recipe_by_id(recipe_id)

        # Assert
        assert isinstance(result, Recipe)

    def test_invalid_recipe_id(self):

        """Returns None when given an invalid recipe id"""
        """Happy path test"""

        # Arrange
        recipe_id = -1

        # Act
        result = get_recipe_by_id(recipe_id)

        # Assert
        assert result is None

    def test_returns_none_with_deleted_id(self, mocker):

        """Returns None when given a recipe id that is deleted"""
        """Happy path test"""


        # Arrange
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
        session_mock.query.return_value.join.return_value.where.return_value.filter.return_value.one_or_none.return_value = recipe

        # Act
        result = get_recipe_by_id(recipe_id)

        # Assert
        assert result is None

    def test_returns_none_with_unpublished_id(self, mocker):

        """Returns None when given a recipe id that is not published"""
        """Happy path test"""


        # Arrange
        recipe_id = 1
        recipe = Recipe(id=recipe_id, name="Test Recipe",
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

        # Act
        result = get_recipe_by_id(recipe_id)

        #Assert
        assert result is None

    def test_raises_exception_when_no_recipe_found(self, mocker):

        """Raises a RecipeNotFoundException when no recipe is found"""
        """Edge case test"""

        # Arrange

        recipe_id = 1
        mocker.patch('db.connection.get_session')
        session_mock = db.connection.get_session.return_value.__enter__.return_value
        session_mock.query.return_value.join.return_value.where.return_value.filter.return_value.one_or_none.return_value = None

        # Act and Assert
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(recipe_id)

    def test_raises_exception_with_deleted_id(self, mocker):

        """Raises a RecipeNotFoundException when given a recipe id that is deleted"""
        """Edge case test"""

        # Arrange
        recipe_id = 1
        recipe = Recipe(id=recipe_id, name="Test Recipe",
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

        # Act and Assert
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(recipe_id)

    def test_raises_exception_with_unpublished_id(self, mocker):

        """Raises a RecipeNotFoundException when given a recipe id that is not published"""
        """Edge case test"""

        # Arrange
        recipe_id = 1
        recipe = Recipe(id=recipe_id, name="Test Recipe",
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

        # Act and Assert
        with pytest.raises(RecipeNotFoundException):
            get_recipe_by_id(recipe_id)

    def test_returns_none_with_non_integer_id(self, mocker):

        """Returns None when given a recipe id that is not an integer"""
        """Edge case test"""

        # Arrange
        recipe_id = "1"
        mocker.patch("db.connection.get_session")

        # Act
        result = get_recipe_by_id(recipe_id)

        # Assert
        assert result is None

class TestRecipeEndpoints:
    client = TestClient(app)

    @classmethod
    def test_returns_all_recipes_when_database_has_recipes(cls, mocker):

        mocker.patch('features.recipes.operations.get_all_recipes', return_value=[
            Recipe(id=1, name="Recipe 1"),
            Recipe(id=2, name="Recipe 2")])

        response = cls.client.get('/')

        assert response.status_code == 200
        assert response.json() == [{"id": 1, "name": "Recipe 1"}, {"id": 2, "name": "Recipe 2"}]

    @classmethod
    def test_return_empty_list_when_database_has_no_recipes(cls, mocker):

        mocker.patch('features.recipes.operations.get_all_recipes', return_value=[])

        response = cls.client.get('/')

        assert response.status_code == 200
        assert response.json() == []

    @classmethod
    def test_get_recipe_by_id(cls, use_test_db, mocker):
        created_recipe = operations.create_recipe("new")
        get_recipe_spy = mocker.spy(operations, "get_recipe")
        response = cls.client.get(f"/recipies/{created_recipe.id}")
        assert response.status_code == 200
        get_recipe_spy.assert_called_with(created_recipe.id)