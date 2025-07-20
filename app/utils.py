from passlib.context import CryptContext # Password hashing library
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context

def hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password) 

def verify(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)