from sqlalchemy import Column, Integer, String, DateTime, func
from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class Image(DbBaseModel):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(300), unique=True)
    storage_location: Mapped[str] = mapped_column(String(300))
    cloudinary_url: Mapped[str] = mapped_column(String(300))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    uploaded_by: Mapped[str] = mapped_column(String(30))
    uploaded_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
