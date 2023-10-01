from fastapi import Depends, FastAPI, HTTPException,status
from sqlmodel import SQLModel, Session, create_engine,select
from fastapi.middleware.cors import CORSMiddleware
from models import User, Song, Playlist, Favourite
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import os

secret_key = os.getenv("secret_key")
ALGORITHM = "HS256"
access_token_expire_minutes = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
 
db_url = './db.sqlite'
DATABASE_URL = f"sqlite:///{db_url}"
 
app = FastAPI()
 
engine = create_engine(DATABASE_URL, echo=True)
 
SQLModel.metadata.create_all(engine)
 
def get_db():
    with Session(engine) as db:
        yield db
 
def verify_password(plain_pass, hashed_pass):
    return pwd_context.verify(plain_pass,hashed_pass)
 
def get_pasword_hash(password):
    return pwd_context.hash(password)
 
def get_user(db, username: str):
    user = db.exect(select(User).where(User.username == username)).first()
    if user:
        return UserInDb(**user.dict(), hashed_password=user.password)
 
async def get_current_user(db: Session = Depends(get_db), token : str = Depends(oauth2_scheme)):
 
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.itcnow() + timedelta(minutes=15)
        to_encode.update({"exp" : expire})
        encoded_jwt = jwt.encode(to_encode,secret_key,algorithm=ALGORITHM)
        return encoded_jwt
   
class UserInDb(BaseModel):
    hashed_password: str
 
class TokenData(BaseModel):
    username: str = None
 
class Token(BaseModel):
    access_token: str
    token_type: str