from enum import Enum
import uuid

from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class ChatType(Enum):
    PRIVATE = "private"
    GROUP = "group"


class ChatInDB(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    creator_id: Mapped[int]
    type: Mapped[ChatType]
    chat_id_in_mongodb: Mapped[str] = mapped_column(unique=True, index=True, default=lambda: str(uuid.uuid4()))
