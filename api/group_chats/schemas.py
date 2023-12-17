from pydantic import BaseModel
from api.auth.schemas import UserRegSchemaOut
from models import ChatType


class CreateChatSchema(BaseModel):
    title: str


class ChatSchema(BaseModel):
    chat_id: int


class GetChatMessages(BaseModel):
    count: int = 20
    offset: int = 0
    chat_id: int

class ChatInfoSchema(BaseModel):
    id: int
    type: ChatType
    creator_id: int
    title: str

class ChatInfoSchemaOut(BaseModel):
    chat_participants: list[UserRegSchemaOut] = []
    chat_info: ChatInfoSchema