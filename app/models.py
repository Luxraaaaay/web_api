from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, Integer, Text, JSON, UniqueConstraint, Boolean

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True, index=True))
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    hashed_password: str
    role: str = Field(default="player", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    games: List["Game"] = Relationship(back_populates="developer")
    reviews: List["Review"] = Relationship(back_populates="user")
    favorites: List["Favorite"] = Relationship(back_populates="user")

class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    steam_appid: Optional[int] = Field(default=None, sa_column=Column(Integer, unique=True, index=True))
    title: str = Field(sa_column=Column(String, index=True))
    developer_id: Optional[int] = Field(default=None, foreign_key="user.id")

    developers: Optional[list] = Field(default=None, sa_column=Column(JSON))
    publishers: Optional[list] = Field(default=None, sa_column=Column(JSON))
    categories: Optional[list] = Field(default=None, sa_column=Column(JSON))
    genres: Optional[list] = Field(default=None, sa_column=Column(JSON))
    required_age: Optional[int] = Field(default=0)
    n_achievements: Optional[int] = Field(default=0)
    platforms: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_released: bool = Field(default=False, sa_column=Column(Boolean, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    release_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    developer: Optional[User] = Relationship(back_populates="games")
    reviews: List["Review"] = Relationship(back_populates="game")
    favorites: List["Favorite"] = Relationship(back_populates="game")

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    game_id: int = Field(foreign_key="game.id", index=True)
    rating: int = Field(sa_column=Column(Integer))
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="reviews")
    game: Optional[Game] = Relationship(back_populates="reviews")

class Favorite(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uix_user_game"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    game_id: int = Field(foreign_key="game.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional[User] = Relationship(back_populates="favorites")
    game: Optional[Game] = Relationship(back_populates="favorites")