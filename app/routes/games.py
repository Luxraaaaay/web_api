from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Game
from sqlmodel import SQLModel, Field

router = APIRouter()


class GameCreate(SQLModel):
    steam_appid: Optional[int] = None
    title: str
    developer_id: Optional[int] = None
    developers: Optional[list] = None
    publishers: Optional[list] = None
    categories: Optional[list] = None
    genres: Optional[list] = None
    required_age: Optional[int] = 0
    n_achievements: Optional[int] = 0
    platforms: Optional[dict] = None
    is_released: Optional[bool] = False
    description: Optional[str] = None
    release_date: Optional[datetime] = None


class GameUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_released: Optional[bool] = None


@router.get("/", response_model=List[Game])
def list_games(skip: int = 0, limit: int = 20, session: Session = Depends(get_session)):
    statement = select(Game).offset(skip).limit(limit)
    results = session.exec(statement).all()
    return results


@router.get("/{game_id}", response_model=Game)
def get_game(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Game)
def create_game(payload: GameCreate, session: Session = Depends(get_session)):
    game = Game.from_orm(payload) if hasattr(Game, 'from_orm') else Game(**payload.dict())
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


@router.patch("/{game_id}", response_model=Game)
def update_game(game_id: int, payload: GameUpdate, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(game, key, value)
    session.add(game)
    session.commit()
    session.refresh(game)
    return game


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    session.delete(game)
    session.commit()
    return None
