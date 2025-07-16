from passlib.context import CryptContext # Password hashing library
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Password hashing context

def hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    """
    return pwd_context.hash(password) 