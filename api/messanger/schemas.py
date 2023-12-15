from pydantic import BaseModel


class CreateChatSchema(BaseModel):
    title: str
    