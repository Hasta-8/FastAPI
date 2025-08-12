from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ================================================== SCHEMAS FOR USERS ============================================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True  # This allows the model to be used with SQLAlchemy models

# schemas for authentication ==============================================================================================
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ================================================== SCHEMAS FOR POSTS ============================================================
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase): # This schema is used for creating new posts
    pass

class PostResponse(PostBase): # This schema is used for returning posts
    id: int
    created_at: datetime
    user_id: int
    user: UserResponse

    class Config: # This is used to convert the model to a dictionary
        orm_mode = True  # This allows the model to be used with SQLAlchemy models

# Schema for JWT response sent back by API
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None  # User ID from the token payload
