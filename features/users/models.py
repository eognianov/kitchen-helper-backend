from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from db.models import DbBaseModel


class UserOrm(DbBaseModel):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary())
