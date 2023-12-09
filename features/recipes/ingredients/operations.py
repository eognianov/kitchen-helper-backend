from typing import List, Type

from fastapi import HTTPException
from sqlalchemy import update

import db.connection
from .exceptions import (
    IngredientIntegrityViolation,
    IngredientCategoryNotFoundException,
    IngredientCategoryIntegrityViolation,
    IngredientCategoryNameViolation,
)
from .models import IngredientCategory, Ingredient
from sqlalchemy.exc import IntegrityError

from .input_models import PatchIngredientInputModel, PatchIngredientCategoryInputModel, CreateIngredientCategoryInputModel, CreateIngredientInputModel


def get_all_ingredients_category() -> List[PatchIngredientCategoryInputModel]:

    """Get all ingredients categories
    ...
    :return: list of ingredients categories
    :rtype: List[IngredientCategory]
    """

    with db.connection.get_session() as session:
        return (
            session.query(IngredientCategory)
            .filter(IngredientCategory.is_deleted == False)
            .all()
        )


def get_ingredient_category_by_id(category_id: int) -> Type[PatchIngredientCategoryInputModel]:
    """Get ingredient category by id
    ...
    :return: ingredient category
    :rtype: IngredientCategory
    """

    with db.connection.get_session() as session:
        category = (
            session.query(IngredientCategory)
            .filter(IngredientCategory.id == category_id)
            .first()
        )

        if not category:
            raise IngredientCategoryNotFoundException()
        return category


def update_ingredient_category(
    category_id: int, field: str, value: str, updated_by: str
) -> Type[PatchIngredientCategoryInputModel]:
    """Update ingredient category
    ...
    :return: updated ingredient category
    :rtype: IngredientCategory
    """

    category = get_ingredient_category_by_id(category_id)

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(IngredientCategory)
                .where(IngredientCategory.id == category_id)
                .values({field: value, "updated_by": updated_by})
            )
            setattr(category, field, value)
            session.commit()

            return category
    except IntegrityError as ex:
        raise IngredientCategoryIntegrityViolation(ex)


def create_ingredient_category(name: str, created_by: str) -> Type[PatchIngredientCategoryInputModel]:
    """Create ingredient category
    ...
    :return: created ingredient category
    :rtype: IngredientCategory
    """

    try:
        category = IngredientCategory(name=name, created_by=created_by)
        with db.connection.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
    except IntegrityError as ex:
        raise IngredientCategoryNameViolation(ex)


def create_ingredient(ingredient: CreateIngredientInputModel):
    try:
        db_ingredient = Ingredient(**ingredient.model_dump())

        with db.connection.get_session() as session:
            session.add(db_ingredient)
            session.commit()
            session.refresh(db_ingredient)

        return db_ingredient

    except IntegrityError as ex:
        raise IngredientIntegrityViolation(ex)


def get_ingredient(ingredient_id: int) -> PatchIngredientInputModel:
    with db.connection.get_session() as session:
        ingredient = (
            session.query(Ingredient)
            .filter(Ingredient.id == ingredient_id, Ingredient.is_deleted == False)
            .first()
        )

        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

    return ingredient


def get_all_ingredients(self):
    with db.connection.get_session() as session:
        ingredients = (
            session.query(Ingredient).filter(Ingredient.is_deleted == False).all()
        )

    return ingredients


def update_ingredient(ingredient_id: int, field: str, value: str):
    with db.connection.get_session() as session:
        db_ingredient = (
            session.query(Ingredient)
            .filter(Ingredient.id == ingredient_id, Ingredient.is_deleted == False)
            .first()
        )

        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        try:
            stmt = (
                update(Ingredient)
                .where(Ingredient.id == ingredient_id)
                .values({field: value})
            )
            session.execute(stmt)

            setattr(db_ingredient, field, value)

            session.commit()

            return db_ingredient

        except IntegrityError as exc:
            raise IngredientIntegrityViolation(exc)


def delete_ingredient(ingredient_id: int) -> PatchIngredientInputModel:

    db_ingredient = get_ingredient(ingredient_id)

    if db_ingredient.is_deleted:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    try:
        with db.connection.get_session() as session:
            session.execute(
                update(Ingredient)
                .where(Ingredient.id == ingredient_id)
                .values({"is_deleted": True})
            )
            db_ingredient.is_deleted = True

            session.commit()
            session.refresh(db_ingredient)

            return {"message": "Ingredient soft-deleted"}

    except IntegrityError as ex:
        raise IngredientIntegrityViolation(ex)
