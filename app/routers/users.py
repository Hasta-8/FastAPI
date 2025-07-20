from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users",  # Prefix for all routes in this router
    tags=["users"]  # Tags for grouping in the OpenAPI documentation
)

# This part is for users manipulation==============================================================================================
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse) # This endpoint creates a new user
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)  # Hash the password before storing it
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{user_id}", response_model=schemas.UserResponse) # This endpoint retrieves a specific user by their ID
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"user with id {user_id} not found")