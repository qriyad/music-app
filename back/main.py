from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, SQLModel, Session, create_engine
from fastapi.middleware.cors import CORSMiddleware
from models import User, Playlist, Song, Favourite

db_url = './db.sqlite'
DATABASE_URL = f"sqlite:///{db_url}"

app = FastAPI()

engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(engine)

@app.get('/')
async def read_root():
    return 'Hello World'

def get_db():
    with Session(engine) as db:
        yield db