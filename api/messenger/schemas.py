from pydantic import BaseModel


class CreateChatSchema(BaseModel):
    title: str


class ChatSchema(BaseModel):
    chat_id: int


class GetChatMessages(BaseModel):
    count: int = 20
    offset: int = 0
    chat_id: int
