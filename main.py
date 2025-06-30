from fastapi import FastAPI
from fastapi import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Post(BaseModel):
    Title: str
    Content: str
    Published: bool = True
    Rating: Optional[int] = None

@app.get("/")
def read_root():
    return {"message": "Hello, Ranchi!"}

@app.get("/posts")
def get_posts():
    return {"data": "This is your posts data"}

@app.post("/create-post")
def create_post(post: Post):
    print(post.Rating)
    print(post.dict())
    return {"data": post}




