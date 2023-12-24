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


class UnauthorizedAccessException(Exception):
    ...
