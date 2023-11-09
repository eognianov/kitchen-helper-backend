from sqlalchemy import Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

Base = declarative_base()

class Ingredient(DbBaseModel):

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key= True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    calories: Mapped[float] = mapped_column(Float, nullable=False)
    carbo: Mapped[float] = mapped_column(Float, nullable=False)
    fats: Mapped[float] = mapped_column(Float, nullable=False)
    protein: Mapped[float] = mapped_column(Float, nullable=False)
    cholesterol: Mapped[float] = mapped_column(Float, nullable=False)
    measurement: Mapped[float] = mapped_column(Float, nullable=False)
    is_deleted: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)