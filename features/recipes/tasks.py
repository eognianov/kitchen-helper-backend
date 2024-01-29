import configuration
import db.connection
import khLogging
from features.recipes.operations import (
    create_category,
    patch_recipe,
    create_or_get_ingredient,
    create_recipe,
    get_all_recipe_categories,
    get_all_ingredients_from_db,
)
from features.recipes.exceptions import CategoryNameViolationException
from features.users.operations import get_user_from_db
from features.recipes.models import Recipe, RecipeInstruction
from features.recipes.input_models import (
    PatchRecipeInputModel,
    IngredientInput,
    RecipeIngredientInputModel,
    CreateInstructionInputModel,
)
from common.authentication import AuthenticatedUser, get_system_user_id
from features.recipes.constants import DEFAULT_PROMPT, GET_RECIPE_PROMPT
from configuration import celery
from sqlalchemy import and_, or_, update
from openai import OpenAI
from datetime import datetime, timedelta
from typing import Type, Tuple
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


def _get_recipes_for_summary_generation() -> list[Type[Recipe]]:
    with db.connection.get_session() as session:
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

        return (
            session.query(Recipe)
            .filter(
                and_(
                    Recipe.is_deleted.is_(False),
                    or_(
                        and_(Recipe.updated_on >= ten_minutes_ago, Recipe.updated_by != get_system_user_id()),
                        Recipe.summary.is_(None),
                    ),
                )
            )
            .all()
        )


@celery.task
def generate_recipe_summary():
    """Call Open Ai to generate recipes summary"""
    logging.info("Start generate summary")

    client = OpenAI(api_key=configuration.OpenAi().chatgpt_api_key)

    recipes = _get_recipes_for_summary_generation()
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
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        generated_summary = completion.choices[0].message.content
        logging.info(f"Generated summary for recipe with id {recipe.id}")
        logging.info(generated_summary)
        patch_model = PatchRecipeInputModel(field='summary', value=generated_summary[:1000])
        patch_recipe(
            recipe_id=recipe.id, patch_input_model=patch_model, patched_by=AuthenticatedUser(id=get_system_user_id())
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
                        or_(RecipeInstruction.updated_by != system_user_id, RecipeInstruction.updated_by.is_(None)),
                        RecipeInstruction.updated_on >= ten_minutes_ago,
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


def _parse_instruction(instruction_string: str):
    delimiter = "@@"
    instruction, complexity, time_to_prepare, category = (
        instruction_string.lstrip(delimiter).rstrip(delimiter).split(delimiter)
    )
    return {"instruction": instruction, "complexity": complexity, "time": time_to_prepare, "category": category}


def _parse_ingredient(ingredient_str: str):
    delimiter = "##"
    measurement, quantity, name, category, calories, carbo, fats, protein, cholesterol = (
        ingredient_str.lstrip(delimiter).rstrip(delimiter).split(delimiter)
    )
    return {
        "measurement": measurement,
        "quantity": quantity,
        "name": name,
        "category": category,
        "calories": calories,
        "carbo": carbo,
        "fats": fats,
        "protein": protein,
        "cholesterol": cholesterol,
    }


def _parse_chatgpt_recipe_response(chat_gpt_response: str) -> Tuple[str, str, int, list[dict], list[dict]]:
    lines = [_.strip() for _ in chat_gpt_response.strip().splitlines() if _]
    name, category, serves = lines[0].rstrip("###").lstrip('###').split('###')
    serves = int(serves)
    instructions = [
        _parse_instruction(_) for _ in lines[lines.index("Instructions:") + 1 : lines.index("Ingredients:")]
    ]
    ingredients = [_parse_ingredient(_) for _ in lines[lines.index("Ingredients:") + 1 :]]
    return name, category, serves, instructions, ingredients


def _get_recipe(excluded_names: list[str] = None):
    client = OpenAI(api_key=configuration.OpenAi().chatgpt_api_key)
    prompt = GET_RECIPE_PROMPT
    if excluded_names:
        exclude_names_prompt = f"\nDo not suggest me any recipe from this list {' ,'.join(excluded_names)}"
        prompt += exclude_names_prompt
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content


def _get_category_to_id_mapping():
    categories = get_all_recipe_categories()
    return {c.name.upper(): c.id for c in categories}


def _get_ingredient_to_id_mapping():
    ingredients = get_all_ingredients_from_db()
    return {i.name.upper(): i.id for i in ingredients}


def _get_recipe_names() -> list[str]:
    with db.connection.get_session() as session:
        recipes = session.query(Recipe.name)

    return [_.name for _ in recipes]


@celery.task
def generate_recipes(count: int = 1):
    """
    Celery task for call ChatGPT and generate recipes

    :param count:
    :return:
    """

    recipes_categories_to_id = _get_category_to_id_mapping()
    ingredients_name_to_id = _get_ingredient_to_id_mapping()
    existing_recipes = _get_recipe_names()
    logging.info("Start generate recipe")
    recipes_added = []
    for _ in range(count):
        try:
            recipe_ingredient_input_models = []
            recipe_instruction_input_models = []
            recipe_response = _get_recipe(excluded_names=existing_recipes)
            name, category, serves, instructions, ingredients = _parse_chatgpt_recipe_response(recipe_response)
            if name.casefold() in existing_recipes:
                logging.info(f"Skipping {name}. Already existing")
            logging.info(f"New recipe name: {name}")
            existing_recipes.append(name)
            category_id = recipes_categories_to_id.get(category.upper())
            if not category_id:
                new_category = create_category(category, get_system_user_id())
                category_id = new_category.id
                recipes_categories_to_id[category.upper()] = category_id
            for _ingredient in ingredients:
                ingredient_id = ingredients_name_to_id.get(_ingredient.get('name').upper())
                if not ingredient_id:
                    ingredient = create_or_get_ingredient(IngredientInput(**_ingredient), get_system_user_id())
                    ingredients_name_to_id[ingredient.name.upper()] = ingredient.id
                    ingredient_id = ingredient.id
                recipe_ingredient_input_models.append(
                    RecipeIngredientInputModel(
                        ingredient_id=ingredient_id, quantity=float(_ingredient.get("quantity", 0))
                    )
                )
            for instruction in instructions:
                recipe_instruction_input_models.append(CreateInstructionInputModel(**instruction))

                recipe = create_recipe(
                    name=name,
                    created_by=AuthenticatedUser(id=get_system_user_id()),
                    category_id=category_id,
                    serves=serves,
                    instructions=recipe_instruction_input_models,
                    ingredients=recipe_ingredient_input_models,
                )
                recipes_added.append(recipe.id)
                logging.info(f"Recipe added. Id: {recipe.id}")
        except Exception as e:
            logging.exception(f"Recipe creation failed! {e}")

        with db.connection.get_session() as session:
            logging.info("Publish all new recipes")
            if recipes_added:
                session.execute(
                    update(Recipe)
                    .values(
                        {
                            "is_published": True,
                            "published_on": datetime.utcnow(),
                            "published_by": get_system_user_id(),
                            "updated_by": get_system_user_id(),
                        }
                    )
                    .where(Recipe.id.in_(recipes_added))
                )
