from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column
from core import Base


class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"


class Chats(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    creator_id: Mapped[int]
    type: Mapped[ChatType]
