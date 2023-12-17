from pydantic import BaseModel
from api.auth.schemas import UserRegSchemaOut
from models import ChatType


class ChatSchema(BaseModel):
    chat_id: int


class CreateChatSchema(BaseModel):
    title: str


class GetChatMessages(BaseModel):
    count: int = 20
    offset: int = 0
    chat_id: int
