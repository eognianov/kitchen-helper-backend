"""Recipe constants"""


INGREDIENT_MEASUREMENT_UNITS = (
    # Metric units
    'KG',
    'GRAM',
    'LITER',
    'MILLILITER',
    'TEASPOON',
    'TABLESPOON',
    'CUP',
    # Imperial units
    'PINCH',
    'PIECE',
    'OUNCE',
    'POUND',
    'FLUID OUNCE',
    'GALLON',
    'QUART',
    'PINT',
)

INGREDIENT_CATEGORIES = (
    'PANTRY ESSENTIALS',
    'VEGETABLES AND GREENS',
    'FRUITS',
    'MEAT AND POULTRY',
    'SEAFOOD',
    'DAIRY',
    'SPICES AND SEASONINGS',
    'GRAINS AND PASTA',
    'CONDIMENTS',
    'BAKING INGREDIENTS',
    'BEVERAGES',
    'NUTS AND SEEDS',
    'SWEETENERS',
    'SNACKS',
    'MISCELLANEOUS',
)

DEFAULT_PROMPT = """
Generate a recipe summary for a dish using the provided steps and list of ingredients. 
Recipe summary must be up to 900 characters long.
I want the recipe summary to be like waiter or chef tries to sell this dish to e customer. 
I will provide the dish information such as name, category, time to prepare and etc.
The steps for preparing will be in this message, with each step starting with ###.
Products will be listed starting with $$$.
"""
