import os
import jwt
from datetime import timedelta, datetime
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from passlib.context import CryptContext


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_DAYS = 30
expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

bearer_scheme = HTTPBearer()

 
def create_access_token(data: dict): #, expires_delta: timedelta
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(authorization):
    token = authorization
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=406, content={"detail":"Token has expired"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail":"Invalid token"})
    

#hash password

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)