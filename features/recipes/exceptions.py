"""Recipes and Ingredients feature exceptions"""


class IngredientCategoryNotFoundException:
    pass


class IngredientCategoryIntegrityViolation:
    pass


class IngredientCategoryNameViolation:
    pass


class IngredientIntegrityViolation:
    pass


class IngredientNotFoundException:
    pass


class IngredientNameViolationException:
    pass


class RecipesCategoryNotFoundException(Exception):
    ...


class RecipesCategoryNameViolationException(Exception):
    ...


class RecipeNotFoundException(Exception):
    ...


class InstructionNotFoundException(Exception):
    ...


class InstructionNameViolationException(Exception):
    ...


class RecipeWithInstructionNotFoundException(Exception):
    ...
