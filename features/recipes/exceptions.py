"""Recipes and Ingredients feature exceptions"""


class IngredientCategoryNotFoundException(Exception):
    pass


class IngredientCategoryIntegrityViolation(Exception):
    pass


class IngredientCategoryNameViolation(Exception):
    pass


class IngredientNotFoundException(Exception):
    pass


class IngredientNameViolationException(Exception):
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


class UnauthorizedAccessException(Exception):
    ...
