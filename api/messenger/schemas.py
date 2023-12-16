from pydantic import BaseModel


class CreateChatSchema(BaseModel):
    title: str


class ChatSchema(BaseModel):
    chat_id: str
