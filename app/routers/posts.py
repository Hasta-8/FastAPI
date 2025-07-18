from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()


# This part is for posts manipulation==============================================================================================
@router.get("/")
def read_root():
    return {"message": "Hello, Ranchi!"}

@router.get("/posts", response_model=List[schemas.PostResponse]) # This endpoint returns all posts
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse) # This endpoint creates a new post
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # new_post = models.post(               
    #     title=post.title,
    #     content=post.content,
    #     published=post.published,
    #     rating=post.rating
    # )
    new_post = models.Post(**post.model_dump())  # Unpack the Post model into a dictionary. Shortcut for the above commented code.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # Refresh to get the new post with its ID. Equivalent to RETURNING * in raw SQL.
    return new_post

@router.get("/posts/{post_id}", response_model=schemas.PostResponse) # This endpoint retrieves a specific post by its ID
def get_a_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"post with id {post_id} not found")

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT) # This endpoint deletes a post by its ID
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {post_id} not found")
    db.delete(post)
    db.commit()
    return

@router.put("/posts/{post_id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse) # This endpoint updates an existing post by its ID
def update_post(post_id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
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
    return post_to_update