from sqlalchemy import Integer, String, Float, Boolean, DateTime, func
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import datetime

class IngredientCategory(DbBaseModel):

    """Ingredient category model"""

    __tablename__ = "INGREDIENT_CATEGORIES"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True, init=False
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_by: Mapped[str] = mapped_column(String(30))
    created_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), init=False
    )
    updated_by: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, init=False
    )
    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        init=False,
    )
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient", back_populates="ingredient", init=False, lazy="selectin"
    )


class MeasurementUnits(Enum):
    KG = 'kg'
    ML = 'ml'
    G = 'g'
    L = 'L'
    OZ = 'oz'
    LB = 'lb'
    CUP = 'cup'


class Ingredient(DbBaseModel):
    __tablename__ = "INGREDIENTS"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    carbo: Mapped[float] = mapped_column(Float, nullable=False)
    fats: Mapped[float] = mapped_column(Float, nullable=False)
    protein: Mapped[float] = mapped_column(Float, nullable=False)
    cholesterol: Mapped[float] = mapped_column(Float, nullable=False)
    measurement: Mapped[str] = mapped_column(SQLAlchemyEnum(MeasurementUnits), nullable=False)
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    deleted_on: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, init=False
    )
    deleted_by: Mapped[Optional[str]] = mapped_column(String, nullable=True, init=False)
