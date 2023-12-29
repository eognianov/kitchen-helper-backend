import db.connection
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from .models import Recipe
from typing import Type
from openai import OpenAI
import configuration

# Set your OpenAI API key
API_KEY = configuration.OpenAi().chatgpt_api_key

DEFAULT_PROMPT = """ Генерирай ми обобщение на рецепта до 300 символа. Аз ще ти подам името на рецептата,
 стъпките за изпълнение и съставките ѝ.
  Ще подам съставките инструкциите на нов ред във формат ##текст##категория###време###сложност###. """


def get_recipes_updated_last_10_min() -> list[Type[Recipe]]:
    with db.connection.get_session() as session:
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)

        all_filtered_recipes = (
            session.query(Recipe)
            .filter(
                and_(
                    Recipe.is_deleted.is_(False),
                    or_(Recipe.created_on >= ten_minutes_ago, Recipe.updated_on >= ten_minutes_ago),
                )
            )
            .all()
        )

    return all_filtered_recipes


def generate_recipe_summary():
    client = OpenAI(api_key=API_KEY)

    recipes = get_recipes_updated_last_10_min()

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
