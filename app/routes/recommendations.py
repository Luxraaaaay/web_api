from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Game, Favorite, Review, User
from app.deps import get_current_user

router = APIRouter()


@router.get("/popular")
def popular_recommendations(limit: int = 20, session: Session = Depends(get_session)):
    # simple popularity: favorites count + reviews count + avg rating
    fav_subq = select(Favorite.game_id, func.count(Favorite.id).label('fav_count')).group_by(Favorite.game_id).subquery()
    rev_subq = select(Review.game_id, func.count(Review.id).label('rev_count'), func.avg(Review.rating).label('avg_rating')).group_by(Review.game_id).subquery()
    stmt = select(Game).outerjoin(fav_subq, Game.id == fav_subq.c.game_id).outerjoin(rev_subq, Game.id == rev_subq.c.game_id).limit(limit)
    games = session.exec(stmt).all()
    return games


@router.get("/personal")
def personal_recommendations(current_user: User = Depends(get_current_user), limit: int = 20, session: Session = Depends(get_session)):
    # simple rule-based: find user's top genres from favorites and reviews
    favs = session.exec(select(Favorite).where(Favorite.user_id == current_user.id)).all()
    genre_counts = {}
    for f in favs:
        g = session.get(Game, f.game_id)
        if g and g.genres:
            for gen in g.genres:
                genre_counts[gen] = genre_counts.get(gen, 0) + 1

    # fallback: if no favorites, use user's review genres
    if not genre_counts:
        revs = session.exec(select(Review).where(Review.user_id == current_user.id)).all()
        for r in revs:
            g = session.get(Game, r.game_id)
            if g and g.genres:
                for gen in g.genres:
                    genre_counts[gen] = genre_counts.get(gen, 0) + 1

    if not genre_counts:
        # fallback to popular
        return popular_recommendations(limit=limit, session=session)

    # pick top genres and recommend games in those genres that user hasn't favorited
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    genres = [g for g, _ in top_genres[:3]]
    stmt = select(Game)
    # filter by genres - any match
    cond = None
    for gen in genres:
        if cond is None:
            cond = Game.genres.like(f'%"{gen}"%')
        else:
            cond = cond | Game.genres.like(f'%"{gen}"%')
    if cond is not None:
        stmt = stmt.where(cond)
    stmt = stmt.limit(limit)
    results = session.exec(stmt).all()
    return results
