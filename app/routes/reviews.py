from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Review, Game, User
from sqlmodel import SQLModel
from app.deps import get_current_user
from app.models import ReviewLike
from fastapi import status

router = APIRouter()


class ReviewCreate(SQLModel):
    rating: int
    content: Optional[str] = None


@router.get("/games/{game_id}/reviews", response_model=List[Review])
def list_reviews(game_id: int, skip: int = 0, limit: int = 50, session: Session = Depends(get_session)):
    statement = select(Review).where(Review.game_id == game_id).offset(skip).limit(limit)
    results = session.exec(statement).all()
    return results


@router.post("/games/{game_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=Review)
def create_review(game_id: int, payload: ReviewCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    review = Review(user_id=current_user.id, game_id=game_id, rating=payload.rating, content=payload.content)
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.post("/{review_id}/like", status_code=status.HTTP_201_CREATED)
def like_review(review_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    existing = session.exec(select(ReviewLike).where((ReviewLike.user_id == current_user.id) & (ReviewLike.review_id == review_id))).first()
    if existing:
        return {"detail": "already liked"}

    like = ReviewLike(user_id=current_user.id, review_id=review_id)
    session.add(like)
    session.commit()
    session.refresh(like)
    return {"id": like.id, "review_id": review_id}


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    session.delete(review)
    session.commit()
    return None
