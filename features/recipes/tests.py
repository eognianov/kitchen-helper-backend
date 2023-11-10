import pytest
import db.connection
from tests.fixtures import use_test_db
from features.recipes import operations
from features.recipes.models import RecipeCategory
from features.recipes.exceptions import CategoryNameViolationException, CategoryNotFoundException


class TestCategoryOperations:
    def test_create_category_success(self, use_test_db):
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