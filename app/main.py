from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

# Database connection setup using psycopg2
max_retries = 5
retries = 0

while retries < max_retries:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="firstinstance",
            cursor_factory=RealDictCursor  # gives dict-like results
        )
        cursor = conn.cursor()
        print("Connected to the database successfully!")
        break
    except Exception as error:
        print("Error connecting to the database:", error)
        print("Retrying in 2 seconds...\n")
        time.sleep(2)
        retries += 1

if retries == max_retries:
    raise Exception("Could not connect to the database after several attempts.")

@app.get("/")
def read_root():
    return {"message": "Hello, Ranchi!"}

# SQLAlchemy test endpoint
#@app.get("/sqlalchemy-test")
#def sqlalchemy_test(db: Session = Depends(get_db)):
#    posts = db.query(models.Post).all()
#    return {"data": posts}

@app.get("/posts") # This endpoint returns all posts
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    # new_post = models.Post(               
    #     title=post.Title,
    #     content=post.Content,
    #     published=post.Published,
    #     rating=post.Rating
    # )
    new_post = models.Post(**post.model_dump())  # Unpack the Post model into a dictionary. Shortcut for the above commented code.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Refresh to get the new post with its ID. Equivalent to RETURNING * in raw SQL.
    return {"data": new_post}

@app.get("/posts/{post_id}") # This endpoint retrieves a specific post by its ID
def get_a_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        return {"requested post": post}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"post with id {post_id} not found")

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT) # This endpoint deletes a post by its ID
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {post_id} not found")
    db.delete(post)
    db.commit()
    return

@app.put("/posts/{post_id}", status_code=status.HTTP_202_ACCEPTED) # This endpoint updates an existing post by its ID
def update_post(post_id: int, updated_post: Post, db: Session = Depends(get_db)):
    post_to_update = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {post_id} not found")
    # db.query(models.Post).filter(models.Post.id == post_id).update(
    #     {
    #         "title": post.title,
    #         "content": post.content,
    #         "published": post.published,
    #         "rating": post.rating
    #     }
    # )
    db.query(models.Post).filter(models.Post.id == post_id).update(updated_post.model_dump()) # Shortcut for the above commented code.
    db.commit()
    db.refresh(post_to_update) # post_to_update is now updated with the new values
    return {"data": post_to_update}


