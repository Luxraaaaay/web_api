from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Favorite, Game, User
from sqlmodel import SQLModel, Field
from app.deps import get_current_user

router = APIRouter()


class FavoriteCreate(SQLModel):
    pass


@router.get("/users/me", response_model=List[Favorite])
def list_my_favorites(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Favorite).where(Favorite.user_id == current_user.id)
    results = session.exec(statement).all()
    return results


@router.post("/games/{game_id}/favorite", status_code=status.HTTP_201_CREATED, response_model=Favorite)
def add_favorite(game_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    existing = session.exec(select(Favorite).where((Favorite.user_id == current_user.id) & (Favorite.game_id == game_id))).first()
    if existing:
        return existing

    fav = Favorite(user_id=current_user.id, game_id=game_id)
    session.add(fav)
    session.commit()
    session.refresh(fav)
    return fav


@router.delete("/games/{game_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(game_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    fav = session.exec(select(Favorite).where((Favorite.user_id == current_user.id) & (Favorite.game_id == game_id))).first()
    if not fav:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
    session.delete(fav)
    session.commit()
    return None
