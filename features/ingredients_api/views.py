from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Ingredient

engine = create_engine("sqlite://ingredients.db")
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine)

router = APIRouter()

class IngredientCreate(BaseModel):

    name:str
    category:str
    calories:float
    carbo:float
    fats:float
    protein:float
    cholesterol:float
    measurement:str

class IngredientResponse(IngredientCreate):
    id:int


class IngredientView:

    def __init__(self):
        pass

    def create_ingredient(ingredient: IngredientCreate):
        db_ingredient = Ingredient(**ingredient.dict())

        with SessionLocal() as session:
            session.add(db_ingredient)
            session.commit()
            session.refresh(db_ingredient)

        return db_ingredient

    def get_ingredient(ingredient_id: int):
        with SessionLocal() as session:
            ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id,
                                                          Ingredient.is_deleted == False).first()

            if not ingredient:
                raise HTTPException(status_code=404, detail="Ingredient not found")

        return ingredient

    def get_all_ingredients():
        with SessionLocal() as session:
            ingredients = session.query(Ingredient).filter(Ingredient.is_deleted == False).all()

        return ingredients

    def update_ingredient(ingredient_id: int, ingredient: IngredientCreate):

        with SessionLocal() as session:

            db_ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id,
                                                             Ingredient.is_deleted == False).first()

            if not db_ingredient:
                raise HTTPException(status_code=404, detail="Ingredient not found")

            for field, value in ingredient.dict().items():
                setattr(db_ingredient, field, value)

                session.commit()
                session.refresh(db_ingredient)

        return db_ingredient

    def soft_delete_ingredient(ingredient_id: int):

        with SessionLocal as session:
            db_ingredient = session.query(Ingredient).filter(Ingredient.id == ingredient_id,
                                                             Ingredient.is_deleted == False).first()

            if not db_ingredient:
                raise HTTPException(status_code=404, detail="Ingredient not found")

            db_ingredient.is_deleted = True

            session.commit()

        return {"message": "Ingredient soft-deleted"}

ingredients_view = IngredientView()

@router.post("/ingredients/", response_model=IngredientResponse)
def create_ingredient(ingredient: IngredientCreate):
    return ingredients_view.create_ingredient(ingredient)

@router.get("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int):
    return ingredients_view.get_ingredient(ingredient_id)

@router.get("/ingredients/", response_model=list[IngredientResponse])
def get_all_ingredients():
    return ingredients_view.get_all_ingredients()

@router.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(ingredient_id: int, ingredient: IngredientCreate):
    return ingredients_view.update_ingredient(ingredient_id, ingredient)

@router.delete("/ingredients/{ingredient_id}", response_model=dict)
def delete_ingredient(ingredient_id: int):
    return ingredients_view.delete_ingredient(ingredient_id)