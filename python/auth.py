from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional


# Get our environment variables
load_dotenv()

# Set up our database session
password = os.getenv('PG_PASSWORD')
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{password}@localhost:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic User model. Necessary to use for the api and SQLAlchemy.
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    plaid_access_token = Column(String, nullable=True)
    plaid_user_token = Column(String, nullable=True)
    plaid_item_id = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# Password hashing with the bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings, 30 minutes expiration
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Further Pydantic models for the JWT token, note that access_token here is referring to the JWT token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Function called from the api, which creates the JWT token by encoding the data with the secret key and algorithm. Uses the jwt library from python-jose.
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify the password against the hashed password using the bcrypt algorithm.
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to get the user from the database session based on the username.
def get_user(username: str):
    db = SessionLocal()
    return db.query(User).filter(User.username == username).first()

# Authenticate works by getting the user from the database, and then verifying the password against the hashed password.
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Function to get the current user from the JWT token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# This works by using the fatstapi bearer token dependency, upon extracting the jwt token 
# from every request. It then decodes the token with the secret key and algorithm, and then
# verifies that the username is in the database. If any of these steps fail, it raises an
# unauthorized exception. If it passes, it returns the user.
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user