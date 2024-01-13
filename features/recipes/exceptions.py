"""Recipes feature exceptions"""


class CategoryNotFoundException(Exception):
    ...


class CategoryNameViolationException(Exception):
    ...


class RecipeNotFoundException(Exception):
    ...


class InstructionNotFoundException(Exception):
    ...


class InstructionNameViolationException(Exception):
    ...


class RecipeWithInstructionNotFoundException(Exception):
    ...


class IngredientDoesNotExistException(Exception):
    def __init__(self, text):
        self.text = text


class RecipeIngredientDoesNotExistException(Exception):
    ...


class IngredientAlreadyInRecipe(Exception):
    ...
