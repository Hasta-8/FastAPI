from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# schemas for post manipulation ==============================================================================================
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

class PostCreate(PostBase): # This schema is used for creating new posts
    pass

class PostResponse(PostBase): # This schema is used for returning posts
    id: int
    created_at: datetime

    class Config: # This is used to convert the model to a dictionary
        orm_mode = True  # This allows the model to be used with SQLAlchemy models

# schemas for user manipulation ==============================================================================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True  # This allows the model to be used with SQLAlchemy models
