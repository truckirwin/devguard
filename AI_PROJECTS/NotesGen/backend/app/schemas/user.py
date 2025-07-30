from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    home_directory: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: Optional[int] = None
    hashed_password: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 