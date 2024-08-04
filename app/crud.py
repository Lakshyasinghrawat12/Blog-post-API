from .database import db
from .models import BlogPost, BlogPostResponse
from .schemas import BlogPostCreate
from bson.objectid import ObjectId

def create_blog_post(blog_post: BlogPostCreate, author: str):
    blog_post_dict = blog_post.dict()
    blog_post_dict["author"] = author
    result = db.posts.insert_one(blog_post_dict)
    return str(result.inserted_id)

def get_blog_posts():
    posts = db.posts.find()
    return [BlogPostResponse(**post) for post in posts]

async def get_blog_post(post_id: str):
    post =  db.posts.find_one({"_id": ObjectId(post_id)})
    if post:
        return {
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "tags": post["tags"],
            "author": post["author"]
        }
    return None


def update_blog_post(post_id: str, blog_post: BlogPostCreate):
    result = db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": blog_post.dict()}
    )
    return result.modified_count > 0

def delete_blog_post(post_id: str):
    result = db.posts.delete_one({"_id": ObjectId(post_id)})
    return result.deleted_count > 0


# curl --location 'http://127.0.0.1:8000/register' \
# --header 'Content-Type: application/json' \
# --data-raw '{
#     "username": "testuser1",
#     "password": "testuser1@"
# }'