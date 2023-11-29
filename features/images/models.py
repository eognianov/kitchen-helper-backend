from sqlalchemy import Integer, String, DateTime, func, Boolean
from features import DbBaseModel
from sqlalchemy.orm import Mapped, mapped_column
import datetime
from typing import Optional


class Image(DbBaseModel):
    __tablename__ = "IMAGES"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True, init=False
    )
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    uploaded_by: Mapped[int] = mapped_column(Integer)
    uploaded_on: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), init=False
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, init=False
    )
    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        init=False,
    )
    in_cloudinary: Mapped[bool] = mapped_column(Boolean, default=False)
