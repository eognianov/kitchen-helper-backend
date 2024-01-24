import configuration
import db.connection
import khLogging
from features.recipes.operations import create_category, patch_recipe
from features.recipes.exceptions import CategoryNameViolationException
from features.users.operations import get_user_from_db
from features.recipes.models import Recipe, RecipeInstruction
from features.recipes.input_models import PatchRecipeInputModel
from common.authentication import AuthenticatedUser, get_system_user_id
from features.recipes.constants import DEFAULT_PROMPT
from configuration import celery
from sqlalchemy import and_, or_
from openai import OpenAI
from datetime import datetime, timedelta
from typing import Type
from gtts import gTTS

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
            continue
    return "Finished adding categories to the database."


def _get_recipes_updated_last_10_min() -> list[Type[Recipe]]:
    with db.connection.get_session() as session:
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

        return (
            session.query(Recipe)
            .filter(
                and_(
                    Recipe.is_deleted.is_(False),
                    or_(Recipe.created_on >= ten_minutes_ago, Recipe.updated_on >= ten_minutes_ago),
                    Recipe.updated_by != get_system_user_id(),
                )
            )
            .all()
        )


@celery.task
def generate_recipe_summary():
    """Call Open Ai to generate recipes summary"""
    logging.info("Start generate summary")

    client = OpenAI(api_key=configuration.OpenAi().chatgpt_api_key)

    recipes = _get_recipes_updated_last_10_min()
    logging.info(f"Recipes created or updated in the last 10 minutes {len(recipes)}")
    for recipe in recipes:
        prompt = DEFAULT_PROMPT
        prompt += f"Name: {recipe.name}" + '\n'
        prompt += f"Category: {recipe.category.name}" + '\n'
        prompt += f"Time to prepare: {recipe.time_to_prepare}" + '\n'
        prompt += f"Complexity: {recipe.complexity}" + '\n'
        prompt += f"Serves: {recipe.serves}" + '\n'
        prompt += f"Calories: {recipe.calories}" + '\n'
        prompt += f"Carbo: {recipe.carbo}" + '\n'
        prompt += f"Fats: {recipe.fats}" + '\n'
        prompt += f"Cholesterol: {recipe.cholesterol}" + '\n'

        for instruction in recipe.instructions:
            prompt += f"###{instruction.category}| {instruction.instruction}" + '\n'

        for ingredient_mapping in recipe.ingredients:
            ingredient = ingredient_mapping.ingredient
            prompt += (
                f"$$${ingredient_mapping.quantity} {ingredient.measurement} {ingredient.name}({ingredient.category})"
                + '\n'
            )
        logging.info(f"Generated prompt for recipe with id {recipe.id}")
        logging.info(prompt)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        generated_summary = completion.choices[0].message.content
        logging.info(f"Generated summary for recipe with id {recipe.id}")
        logging.info(generated_summary)
        patch_model = PatchRecipeInputModel(field='summary', value=generated_summary)
        system_user_id = get_system_user_id()
        patch_recipe(
            recipe_id=recipe.id, patch_input_model=patch_model, patched_by=AuthenticatedUser(id=system_user_id)
        )


@celery.task
def generate_instruction_audio_files():
    """
    Celery task to generate or update instruction audio files

    :return:
    """
    with db.connection.get_session() as session:
        system_user_id = get_system_user_id()
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
        recently_updated_instructions = (
            session.query(RecipeInstruction)
            .filter(
                or_(
                    and_(
                        RecipeInstruction.updated_by != system_user_id, RecipeInstruction.updated_on >= ten_minutes_ago
                    ),
                    RecipeInstruction.audio_file.is_(None),
                )
            )
            .all()
        )

        if not recently_updated_instructions:
            logging.info("No instructions to generate audio files.")
            return "No instructions to generate audio files."
        audio_folder = configuration.AUDIO_PATH
        for instruction in recently_updated_instructions:
            audio_file_path = audio_folder.joinpath(f"{instruction.id}.mp3")
            tts = gTTS(text=instruction.instruction, lang="en")
            tts.save(str(audio_file_path))
            instruction.audio_file = f"{instruction.id}.mp3"
            instruction.updated_by = system_user_id
            session.add(instruction)
            session.commit()

            logging.info(f"Audio file generated for instruction {instruction.id}")

    logging.info("Task completed: generate_instruction_audio_files")
    return "Task completed: generate_instruction_audio_files"
