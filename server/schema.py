from typing import List, Union
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class ContactBase(BaseModel):
    contact_name: str
    is_online: bool


class CreateContact(ContactBase):
    pass


class Contact(ContactBase):
    id: int
    contact_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    user_name: str


class CreateUser(UserBase):
    password: str


class User(UserBase):
    id: int
    is_online: bool

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    message_description: Union[str, None] = None


class CreateMessage(MessageBase):
    pass


class Message(MessageBase):
    id: int
    message_id: int
