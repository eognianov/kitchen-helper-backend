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


@celery.task
def calculate_nutrients():
    """
    Celery task to calculate the nutrients for the recipes
    :return:
    """
    with db.connection.get_session() as session:
        recipes = session.query(Recipe).all()
        if not recipes:
            logging.info("No recipes to calculate nutrients")
            return "No recipes to calculate nutrients"
        for recipe in recipes:
            total_calories = 0
            total_carbo = 0
            total_fats = 0
            total_proteins = 0
            total_cholesterol = 0

            for ingredient in recipe.ingredients:
                recipe_ingredient = (
                    session.query(RecipeIngredient)
                    .filter(RecipeIngredient.ingredient_id == ingredient.id, RecipeIngredient.recipe_id == recipe.id)
                    .first()
                )

                total_calories += ingredient.calories * recipe_ingredient.quantity
                total_carbo += ingredient.carbo * recipe_ingredient.quantity
                total_fats += ingredient.fats * recipe_ingredient.quantity
                total_proteins += ingredient.protein * recipe_ingredient.quantity
                total_cholesterol += ingredient.cholesterol * recipe_ingredient.quantity

            recipe.calories = total_calories
            recipe.carbo = total_carbo
            recipe.fats = total_fats
            recipe.proteins = total_proteins
            recipe.cholesterol = total_cholesterol

            session.add(recipe)
            session.commit()
            session.refresh(recipe)

            logging.info(f"Recipe {recipe.id} nutrients updated successfully")

    return "Finished calculating nutrients"
