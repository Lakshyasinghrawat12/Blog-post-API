from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str

class BlogPostCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class BlogPostResponse(BaseModel):
    id: str
    title: str
    content: str
    author: str
    tags: List[str]
