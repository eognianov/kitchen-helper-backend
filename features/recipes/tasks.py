import configuration
import db.connection
import khLogging
from features.recipes.operations import create_category
from features.recipes.exceptions import CategoryNameViolationException
from features.users.operations import get_user_from_db
from features.recipes.models import Recipe, RecipeIngredient
from configuration import celery

logging = khLogging.Logger("celery-recipes-tasks")


@celery.task
def seed_recipe_categories():
    """
    Celery task used to seed the recipe categories
    :return:
    """
    categories = [cat for cat in configuration.AppRecipeCategories().categories]
    user = get_user_from_db(username=configuration.AppUsers().users[0]["username"])
    if not user:
        logging.info("No users found to add categories")
        return "No users found to add categories"
    if not categories:
        logging.info("No categories found")
        return "No categories found"
    for category in categories:
        try:
            new_category = create_category(category_name=category, created_by=user.id)
            logging.info(f"User {user.id} created Category (#{new_category.id}).")
        except CategoryNameViolationException as ex:
            logging.exception(str(ex))
            continue
    return "Finished adding categories to the database."
