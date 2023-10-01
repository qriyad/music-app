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
@app.post('/users/', response_model=User, tags=['Users'])
async def create_user(user: User, db: Session = Depends(get_db)):
    statement = select(User).where(User.email == user.email)
    db_user = db.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db.add(user)
    db.commit()
    db.refresh(user)
    return 'User Created succsessfully'

@app.get("/users/{user_id}", response_model=User, tags=['Users'])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User, tags=['Users'])
async def update_user(user_id: int, user: User, db: Session = Depends(get_db)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_data = user.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return 'User Updated succsessfully'

@app.delete("/users/{user_id}", response_model=User, tags=['Users'])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return 'User Removed Succsessfully'
"""
@app.post('/schedules/', response_model=Schedule, tags=['Schedules'])
async def create_schedule(schedule: Schedule, db: Session = Depends(get_db)):
    user = db.get(User, schedule.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    note = db.get(Note, schedule.note_id)  
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    db_schedule = Schedule.from_orm(schedule)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule
"""