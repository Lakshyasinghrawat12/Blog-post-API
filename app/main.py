from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from .models import BlogPost,User
from fastapi.openapi.utils import get_openapi
from .schemas import UserCreate, BlogPostCreate, BlogPostResponse, UserResponse
from .auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from .crud import create_blog_post, get_blog_posts, get_blog_post, update_blog_post, delete_blog_post
from .database import db

app = FastAPI()

@app.get("/users/{username}")
async def read_user(username: str):
    return {"message": f"Hello {username}"}

@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db.users.insert_one({"username": user.username, "password": hashed_password})
    return {"username": user.username}

@app.post("/posts/", response_model=BlogPostResponse)
async def create_post(blog_post: BlogPostCreate, current_user: User = Depends(get_current_user)):
    post_id = create_blog_post(blog_post, current_user.username)
    return BlogPostResponse(id=post_id, **blog_post.dict(), author=current_user.username)

@app.get("/posts/", response_model=List[BlogPostResponse])
async def read_posts():
    posts = get_blog_posts()
    return posts

@app.get("/posts/{post_id}", response_model=BlogPostResponse)
async def get_post(post_id: str):
    post = await get_blog_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=BlogPostResponse)
async def update_post(post_id: str, blog_post: BlogPostCreate, current_user: User = Depends(get_current_user)):
    if not update_blog_post(post_id, blog_post):
        raise HTTPException(status_code=404, detail="Post not found")
    return BlogPostResponse(id=post_id, **blog_post.dict(), author=current_user.username)

@app.delete("/posts/{post_id}", response_model=dict)
async def delete_post(post_id: str, current_user: User = Depends(get_current_user)):
    if not delete_blog_post(post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"msg": "Post deleted successfully"}


# Define the security scheme
app.openapi_schema = None

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Blog API",
        version="1.0.0",
        description="API for creating and managing blog posts",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi