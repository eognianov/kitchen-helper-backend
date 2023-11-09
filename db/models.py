"""DB Models module"""
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class DbBaseModel(DeclarativeBase, MappedAsDataclass):
    """DB base model"""
    ...
