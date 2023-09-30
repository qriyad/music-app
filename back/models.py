from sqlmodel import Field, SQLModel, Session, create_engine, Relationship
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, foreign_key=True)
    name: str
    surname: str
    create_date: datetime = Field(default_factory=datetime.utcnow)
    username: str
    password: str
    playlists: List["Playlist"] = Relationship(back_populates="user")
    songs: List["Song"] = Relationship(back_populates="user")

class Playlist(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, foreign_key=True)
    song_id: int
    user_id: int
    title: str
    description: str
    image: str
    create_date: datetime = Field(default_factory=datetime.utcnow)
    user: User = Relationship(back_populates="playlists")
    songs: List["Song"] = Relationship(back_populates="playlist")

class Song(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True, foreign_key=True)
    user_id: int
    create_date: datetime = Field(default_factory=datetime.utcnow)
    title: str
    duration: str
    user: User = Relationship(back_populates="songs")
    playlist: Playlist = Relationship(back_populates="songs")

class Favourite(SQLModel, table=True):
    user_id_song_id: Optional[int] = Field(primary_key=True, index=True, foreign_key=True)
    user: User = Relationship(back_populates="favourites")
    song: Song = Relationship(back_populates="favourites")