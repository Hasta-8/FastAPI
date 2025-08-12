from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",  # Prefix for all routes in this router
    tags=["posts"]  # Tags for grouping in the OpenAPI documentation
)


#============================================GET ALL POSTS ========================================================
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10):

    posts = db.query(models.Post).limit(limit).all()
    return posts

#============================================GET ALL POSTS OF A USER========================================================
#@router.get("/all", response_model=List[schemas.PostResponse])
#def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
#    '''
#    The current_user is obtained from the token, which is passed as a dependency to the endpoint.
#    This ensures that the user is authenticated before accessing the posts.
#    '''
#    # Get all posts for the current user
#    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
#    
#    # If user has no posts, return valid message instead of an empty list
#    if not posts:
#        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                            detail="No posts found for the current user")
#    return posts


#============================================CREATE A POST========================================================
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):
    '''
    user_id is obtained from the token, which is passed as a dependency
    to the endpoint. This ensures that the user is authenticated before creating a post.
    '''
    # Unpack the Post model into a dictionary.
    new_post = models.Post(**post.model_dump(), user_id=current_user.id)  
    db.add(new_post)
    db.commit()
    # Refresh to get the new post with its ID. Equivalent to RETURNING * in raw SQL.
    db.refresh(new_post)  
    return new_post

#=============================================GET A PARTICULAR POST========================================================
@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_a_post(post_id: int, db: Session = Depends(get_db), 
               current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if post:
        # Check if the current user is the owner of the post
        # This is to prevent unauthorized access to posts by other users.
        if post.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="Not authorized to perform requested action")
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"post with id {post_id} not found")

#=============================================DELETE A POST========================================================
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {post_id} not found")
    
    # Check if the current user is the owner of the post
    # This is to prevent unauthorized deletion of posts by other users.
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")
    
    db.delete(post)
    db.commit()
    return

#=============================================UPDATE A POST========================================================
@router.put("/{post_id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse)
def update_post(post_id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    post_to_update = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {post_id} not found")
    
    # Check if the current user is the owner of the post
    # This is to prevent unauthorized updation of posts by other users.
    if post_to_update.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")

    db.query(models.Post).filter(models.Post.id == post_id).update(updated_post.model_dump()) # Shortcut for the above commented code.
    db.commit()
    db.refresh(post_to_update) # post_to_update is now updated with the new values
    return post_to_update