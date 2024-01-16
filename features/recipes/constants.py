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
Generate a quick recipe description for a dish using the provided steps and list of ingredients. 
A description must be up to 500 characters and present the main characteristics of the dish.
I will provide the dish information such as name, category, time to prepare and etc.
The steps for preparing will be in this message, with each step starting with ###.
Products will be listed starting with $$$.
"""
