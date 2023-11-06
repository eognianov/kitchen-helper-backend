"""Recipes feature responses"""
import datetime
from typing import Optional

import pydantic


class Category(pydantic.BaseModel):
    """Category response"""
    id: int
    name: str
    created_by: str
    created_on: datetime.datetime
    updated_by: Optional[str] = None
    updated_on: Optional[datetime.datetime] = None
