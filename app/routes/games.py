from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from sqlalchemy import or_, func, desc as sa_desc

from app.database import get_session
from app.models import Game, Review
from sqlmodel import SQLModel, Field
from fastapi import UploadFile, File
from app.models import GameAsset, User
from app.deps import get_current_user
from pathlib import Path
import shutil

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
def list_games(
    skip: int = Query(0, description="Offset for pagination"),
    limit: int = Query(20, description="Maximum items to return"),
    q: Optional[str] = None,
    genre: Optional[str] = None,
    platform: Optional[str] = None,
    is_released: Optional[bool] = None,
    min_rating: Optional[float] = None,
    sort: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """List games with optional search and filters.

    Params:
    - `q`: full-text-ish search on title or description (case-insensitive)
    - `genre`: filter games that include this genre
    - `platform`: filter games that include this platform
    - `is_released`: boolean filter
    - `min_rating`: minimum average rating (requires at least one review)
    - `sort`: field to sort by, e.g. `release_date` or `avg_rating`, append `:desc` for descending
    """

    stmt = select(Game)

    # basic filters
    if q:
        q_pattern = f"%{q}%"
        stmt = stmt.where(or_(Game.title.ilike(q_pattern), Game.description.ilike(q_pattern)))

    if genre:
        # genres is stored as JSON; perform a simple text match for the genre string
        stmt = stmt.where(Game.genres.like(f'%"{genre}"%'))

    if platform:
        stmt = stmt.where(Game.platforms.like(f'%"{platform}"%'))

    if is_released is not None:
        stmt = stmt.where(Game.is_released == bool(is_released))

    # handle min_rating by joining aggregated review averages
    order_by_clause = None
    if min_rating is not None:
        avg_subq = select(Review.game_id, func.avg(Review.rating).label("avg_rating")).group_by(Review.game_id).subquery()
        stmt = select(Game).join(avg_subq, Game.id == avg_subq.c.game_id).where(avg_subq.c.avg_rating >= float(min_rating))

    # sorting
    if sort:
        parts = sort.split(":")
        key = parts[0]
        desc = len(parts) > 1 and parts[1].lower() == "desc"
        if key == "release_date":
            order_by_clause = sa_desc(Game.release_date) if desc else Game.release_date
        elif key == "avg_rating":
            # sort by aggregated rating; join if not already
            avg_subq = select(Review.game_id, func.avg(Review.rating).label("avg_rating")).group_by(Review.game_id).subquery()
            stmt = select(Game, avg_subq.c.avg_rating).join(avg_subq, Game.id == avg_subq.c.game_id)
            order_by_clause = sa_desc(avg_subq.c.avg_rating) if desc else avg_subq.c.avg_rating

    # apply offset/limit
    if order_by_clause is not None:
        stmt = stmt.order_by(order_by_clause)

    stmt = stmt.offset(skip).limit(limit)

    results = session.exec(stmt).all()

    # when join returns tuples (Game, avg) convert to games
    if results and isinstance(results[0], tuple):
        games = [r[0] for r in results]
        return games

    return results


@router.get("/{game_id}", response_model=Game)
def get_game(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


@router.get("/{game_id}/reviews", response_model=List[Review])
def list_game_reviews(game_id: int, skip: int = Query(0, description="Offset for pagination"), limit: int = Query(50, description="Maximum reviews to return"), session: Session = Depends(get_session)):
    statement = select(Review).where(Review.game_id == game_id).offset(skip).limit(limit)
    results = session.exec(statement).all()
    return results


@router.post("/{game_id}/assets", status_code=status.HTTP_201_CREATED)
def upload_game_assets(
    game_id: int,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    # simple permission: allow developer or admin
    if current_user.role != "admin" and game.developer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    out_dir = Path("data") / "assets" / str(game_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    assets = []
    for f in files:
        dest = out_dir / f.filename
        with dest.open("wb") as fd:
            shutil.copyfileobj(f.file, fd)
        asset = GameAsset(game_id=game_id, filename=f.filename, url=str(dest.as_posix()))
        session.add(asset)
        assets.append(asset)

    session.commit()
    for a in assets:
        session.refresh(a)

    return assets


@router.get("/publishers/{publisher_id}/games", response_model=list[Game])
def list_publisher_games(publisher_id: int, session: Session = Depends(get_session)):
    # return games where developer_id == publisher_id or where publishers JSON includes the publisher id/name
    stmt = select(Game)
    results = session.exec(stmt).all()
    filtered = []
    for g in results:
        if g.developer_id == publisher_id:
            filtered.append(g)
            continue
        pubs = g.publishers or []
        try:
            if any(str(publisher_id) == str(x) for x in pubs):
                filtered.append(g)
        except Exception:
            pass

    return filtered


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
