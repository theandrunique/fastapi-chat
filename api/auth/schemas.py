from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    login: str
    password: bytes
    # email: EmailStr
    # active: bool


class UserRegSchemaIn(BaseModel):
    login: str
    password: str


class UserRegSchemaOut(BaseModel):
    id: str
    login: str
