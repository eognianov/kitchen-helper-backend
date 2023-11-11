"""Recipes feature exceptions"""


class CategoryNotFoundException(Exception):
    ...


class CategoryNameViolationException(Exception):
    ...


class RecipeNotFoundException(Exception):
    ...


class InstructionNotFoundException(Exception):
    ...
