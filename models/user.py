from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Users(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    # future
    # custom_id: Mapped[str] = mapped_column(unique=True)
    login: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]