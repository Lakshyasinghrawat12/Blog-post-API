from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    password: str

    class Config:
        allow_population_by_field_name = True

class BlogPost(BaseModel):
    title: str
    content: str
    tags: List[str]

class BlogPostResponse(BlogPost):
    id: str  # Ensure id is a string
    author: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
