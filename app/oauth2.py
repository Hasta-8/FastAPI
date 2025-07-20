# Authentication and Authorization utils using OAuth2 with JWTs
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # OAuth2PasswordBearer is a class that provides a way to extract the token from the request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # Create an instance of OAuth2PasswordBearer

# We need to provide 3 things to encode and decode JWTs:
# 1. Secret key to encode the JWT
# 2. Algorithm to use for encoding
# 3. Expiration time for the JWT

SECRET_KEY = "b9c1f68c-49d2-44eb-8e91-f6a3de79b87a-L@GZ#eV9iT8xKpM2sNqR!wXz$yUtGrFvChDjSkLmPoIiUuYtReWqAsDfGhJkLzXcVbN"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    """
    Create a JWT access token with the given payload and expiration time.
    """
    user_credentials = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Set expiration time
    user_credentials.update({"exp": expire}) # Add expiration time to the payload
    encoded_jwt = jwt.encode(user_credentials, SECRET_KEY, algorithm=ALGORITHM) # Encode the payload with the secret key and algorithm

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """
    Verify the JWT access token and return the payload if valid.
    Raises JWTError if the token is invalid or expired.
    """
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract user ID from the payload
        id: str = payload.get("user_id")
        # If user ID is not found in the payload, raise an exception
        if id is None:
            raise credentials_exception
        # Create a TokenData object with the user ID if found
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    
    return token_data  # Return the TokenData object containing user ID

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Get the current user from the JWT access token.
    Raises HTTPException if the token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token and get the user ID
    token = verify_access_token(token, credentials_exception)  
    # Find the user in the database using the user ID from the token
    user = db.query(models.User).filter(models.User.id == token.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {token.id} not found",
        )
    
    return user
