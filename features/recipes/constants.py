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
# Recipe info
# I want the recipe info to be like waiter or chef tries to sell this dish to e customer. Info can be more verbose but not more than 1000 characters.

GET_RECIPE_PROMPT = """"
For my web application, which is a kitchen recipes database, I want from you to generate me a recipe information in format:  
###Recipe name###Recipe Category###Serves (only digit)###
Then must be a list instructions. Every instruction Must be in the following format:
@@Instruction text@@Complexity (digit from 1 to 5)@@Time to preparte (only digit in minutes)@@Instruction category@@
Before them must have "Instructions:"
The must not be indexes or dashes or type of bullet marks before the instructions
Then must be a list of ingredients. Every ingredient must be in the following format:
##Measurament unit##Quantity##Ingredient##Ingredient category##Calories##Carbs##Fats##Protein##cholesterol##
Before them must have "Ingredients:"
The must not be indexes or dashes or type of bullet marks  before the ingredients
You must not put any additional information or formatting. You do not need to put labels to the values or anything!
"""
