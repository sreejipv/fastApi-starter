# models.py
from typing import Optional
from unicodedata import name
from pydantic import BaseModel, EmailStr


class Item(BaseModel):
    name: str
    link: str
    description: str

class User(BaseModel):
    name: str
    password: str
    email: str

class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB():
    hashed_password: str

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PasswordRecoveryResponse(BaseModel):
    message: str