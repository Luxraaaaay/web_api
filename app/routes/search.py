from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from sqlalchemy import or_

from app.database import get_session
from app.models import Game

router = APIRouter()


@router.get("/", response_model=List[Game])
def search_games(q: Optional[str] = None, genre: Optional[str] = None, platform: Optional[str] = None, skip: int = 0, limit: int = 20, session: Session = Depends(get_session)):
    stmt = select(Game)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(or_(Game.title.ilike(pattern), Game.description.ilike(pattern)))
    if genre:
        stmt = stmt.where(Game.genres.like(f'%"{genre}"%'))
    if platform:
        stmt = stmt.where(Game.platforms.like(f'%"{platform}"%'))
    stmt = stmt.offset(skip).limit(limit)
    results = session.exec(stmt).all()
    return results


@router.get("/suggestions")
def search_suggestions(q: str, limit: int = 10, session: Session = Depends(get_session)):
    # simple prefix-based title suggestions
    pattern = f"{q}%"
    stmt = select(Game.title, Game.id).where(Game.title.ilike(pattern)).limit(limit)
    rows = session.exec(stmt).all()
    suggestions = [{"id": r[1], "title": r[0]} for r in rows]
    return {"suggestions": suggestions}
