from fastapi import HTTPException
from sqlalchemy import update

import db.connection
from .exceptions import IngredientIntegrityViolation
from .models import Ingredient
from .responses import Ingredient
from sqlalchemy.exc import IntegrityError


def create_ingredient(ingredient: Ingredient):

    try:
        db_ingredient = Ingredient(**ingredient.model_dump())

        with db.connection.get_session() as session:
            session.add(db_ingredient)
            session.commit()
            session.refresh(db_ingredient)

        return db_ingredient

    except IntegrityError as ex:
        raise IngredientIntegrityViolation(ex)

def get_ingredient(ingredient_id: int) -> Ingredient:
    with db.connection.get_session() as session:
        ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id,
                                                          Ingredient.is_deleted == False).first()

        if not ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

    return ingredient

def get_all_ingredients(self):

    with db.connection.get_session() as session:
        ingredients = session.query(Ingredient).filter(Ingredient.is_deleted == False).all()

    return ingredients

def update_ingredient(ingredient_id: int, field: str, value: str):

    with db.connection.get_session() as session:

        db_ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id,
                                                             Ingredient.is_deleted == False).first()

        if not db_ingredient:
                raise HTTPException(status_code=404, detail="Ingredient not found")

        try:
            # Build the update statement
            stmt = update(Ingredient).where(Ingredient.id == ingredient_id).values({field: value})
            session.execute(stmt)

            # Update the corresponding attribute in the SQLAlchemy model
            setattr(db_ingredient, field, value)

            # Commit the changes and refresh the model
            session.commit()
            session.refresh(db_ingredient)

            return db_ingredient

        except IntegrityError as exc:

            raise IngredientIntegrityViolation(exc)

def soft_delete_ingredient(ingredient_id: int):

    with db.connection.get_session() as session:
        db_ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id,
                                                             Ingredient.is_deleted == False).first()

        if not db_ingredient:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        try:
            with db.connection.get_session() as session:

                session.execute(update(Ingredient).where(Ingredient.id == ingredient_id).values({"is_deleted": True}))
                db_ingredient.is_deleted = True

                session.commit()
                session.refresh(db_ingredient)

                return {"message": "Ingredient soft-deleted"}

        except IntegrityError as ex:

            raise IngredientIntegrityViolation(ex)
