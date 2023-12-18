from pydantic import BaseModel
from api.auth.schemas import UserRegSchemaOut
from models import ChatType


class ChatSchema(BaseModel):
    chat_id: int


class ChatInfoSchema(BaseModel):
    id: int
    type: ChatType
    creator_id: int
    title: str


class ChatInfoSchemaOut(BaseModel):
    chat_members: list[UserRegSchemaOut] = []
    chat_info: ChatInfoSchema
    total_messages: int
