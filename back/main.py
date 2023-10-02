from fastapi import Depends, FastAPI, HTTPException,status, File, UploadFile
from sqlmodel import SQLModel, Session, create_engine,select
from fastapi.middleware.cors import CORSMiddleware
from models import User, Song, Playlist
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import os
import threading

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
 
thread_local = threading.local()

def get_db():
    if not hasattr(thread_local, "session"):
        thread_local.session = Session(engine)
    return thread_local.session

 
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
    statement = select(User).where(User.username == user.username)
    db_user = db.exec(statement).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_user = User(
        name=user.name,
        surname=user.surname,
        username=user.username,
        password=user.password,  
        create_date=user.create_date
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    os.mkdir(f'users/{user.username}')
    return 'User Created successfully'

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

@app.post('/upload_song/{username}/')
async def upload_song(username: str,playlist_id: int,duration: str, song_f: UploadFile = File(None), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    path = f"users/{username}/{song_f.filename}"
    with open(path, "wb+") as f:
        f.write(song_f.file.read())

    song = Song(
        title=path, 
        duration=duration,
        playlist_id=playlist_id, 
        user_id=user.id
    )
    db.add(song)
    db.commit()
    
    return {"filename": song_f.filename, "user": username}