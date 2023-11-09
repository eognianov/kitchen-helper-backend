from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ingredient(Base):

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key= True, index= True)
    name = Column(String, index=True)
    category = Column(String)
    calories = Column(Float)
    carbo = Column(Float)
    fats = Column(Float)
    protein = Column(Float)
    cholesterol = Column(Float)
    measurement = Column(String)
    is_deleted = Column(Boolean, default=False)