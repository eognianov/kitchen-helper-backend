import diskcache

import configuration
import db.connection
import khLogging
from features import Recipe
from features.recipes.operations import create_category
from features.recipes.exceptions import CategoryNameViolationException
from features.users.operations import get_user_from_db
from features.recipes.models import Recipe, RecipeIngredient
from configuration import celery
from sqlalchemy import and_, or_, text
from openai import OpenAI
from datetime import datetime, timedelta
from typing import Type

logging = khLogging.Logger("celery-recipes-tasks")

CACHE = diskcache.Cache(directory=configuration.CACHE_PATH, disk=diskcache.JSONDisk)


def _get_system_user_id_from_db() -> int:
    with db.connection.get_connection() as connection:
        system_user_id = connection.execute(
            text('SELECT ID FROM "Users" WHERE username = :name'), {'name': 'System'}
        ).scalar()
        return system_user_id


def _get_system_user_id() -> int:
    """
    Get system user id
    :return:
    """

    system_user_id = CACHE.get('system_user_id')
    if not system_user_id:
        system_user_id = _get_system_user_id_from_db()
        CACHE.set('system_user_id', system_user_id)
        return system_user_id


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


DEFAULT_PROMPT = """ Генерирай ми обобщение на рецепта до 300 символа. Аз ще ти подам името на рецептата,
 стъпките за изпълнение и съставките ѝ.
  Ще подам съставките инструкциите на нов ред във формат ##текст##категория###време###сложност###. """


def _get_recipes_updated_last_10_min() -> list[Type[Recipe]]:
    with db.connection.get_session() as session:
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

        all_filtered_recipes = (
            session.query(Recipe)
            .filter(
                and_(
                    Recipe.is_deleted.is_(False),
                    or_(Recipe.created_on >= ten_minutes_ago, Recipe.updated_on >= ten_minutes_ago),
                    Recipe.updated_by != _get_system_user_id(),
                )
            )
            .all()
        )

    return all_filtered_recipes


def generate_recipe_summary():
    client = OpenAI(api_key=configuration.OpenAi().chatgpt_api_key)

    recipes = _get_recipes_updated_last_10_min()

    for recipe in recipes:
        prompt = DEFAULT_PROMPT
        prompt += recipe.name + '\n'

        for instruction in recipe.instructions:
            prompt += (
                f'##{instruction.instruction}'
                f'##{instruction.category}'
                f'##{instruction.time_to_prepare}'
                f'##{instruction.complexity}'
            )

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        generated_summary = completion['choices'][0]['text']

        # Do something with the generated summary
        print(f"Recipe: {recipe.name}\nGenerated Summary: {generated_summary}\n")
