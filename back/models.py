from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    name: str
    surname: str
    create_date: datetime = Field(default_factory=datetime.utcnow)
    username: str
    password: str
    playlists: List["Playlist"] = Relationship(back_populates="user")
    songs: List["Song"] = Relationship(back_populates="user")
    favourites: List["Favourite"] = Relationship(back_populates="user")

class Playlist(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: str
    image: str
    create_date: datetime = Field(default_factory=datetime.utcnow)
    user: User = Relationship(back_populates="playlists")
    songs: List["Song"] = Relationship(back_populates="playlist")

class Song(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    playlist_id: int = Field(foreign_key="playlist.id")
    create_date: datetime = Field(default_factory=datetime.utcnow)
    title: str
    duration: str
    user: User = Relationship(back_populates="songs")
    playlist: Playlist = Relationship(back_populates="songs")
    favourites: List["Favourite"] = Relationship(back_populates="song")

class Favourite(SQLModel, table=True):
    user_id: int = Field(primary_key=True, index=True, foreign_key="user.id")
    song_id: int = Field(primary_key=True, index=True, foreign_key="song.id")
    user: User = Relationship(back_populates="favourites")
    song: Song = Relationship(back_populates="favourites")