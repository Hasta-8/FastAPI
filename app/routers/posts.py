from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",  # Prefix for all routes in this router
    tags=["posts"]  # Tags for grouping in the OpenAPI documentation
)


# This part is for posts manipulation==============================================================================================
@router.get("/", response_model=List[schemas.PostResponse]) # This endpoint returns all posts
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).all()
    return posts

# This endpoint creates a new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):
    
    # user_id is obtained from the token, which is passed as a dependency
    # to the endpoint. This ensures that the user is authenticated before creating a post.
    print(f"User Email: {current_user.email}")  # Debugging line to check current user details
    # Unpack the Post model into a dictionary.
    new_post = models.Post(**post.model_dump())  
    db.add(new_post)
    db.commit()
    # Refresh to get the new post with its ID. Equivalent to RETURNING * in raw SQL.
    db.refresh(new_post)  
    return new_post

# This endpoint retrieves a specific post by its ID
@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_a_post(post_id: int, db: Session = Depends(get_db), 
               current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"post with id {post_id} not found")

# This endpoint deletes a post by its ID
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {post_id} not found")
    db.delete(post)
    db.commit()
    return

# This endpoint updates an existing post by its ID
@router.put("/{post_id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse)
def update_post(post_id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

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