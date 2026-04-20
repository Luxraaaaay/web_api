from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, Favorite, Review
from app.deps import get_current_user

router = APIRouter()


class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    bio: Optional[str]




@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role, "created_at": current_user.created_at}


@router.patch("/me")
def update_me(payload: UserUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    update_data = payload.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(current_user, k, v)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role}


@router.get("/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role, "created_at": user.created_at}


@router.get("/{user_id}/favorites")
def get_user_favorites(user_id: int, session: Session = Depends(get_session), skip: int = 0, limit: int = 50):
    statement = select(Favorite).where(Favorite.user_id == user_id).offset(skip).limit(limit)
    results = session.exec(statement).all()
    return results


@router.get("/{user_id}/reviews")
def get_user_reviews(user_id: int, session: Session = Depends(get_session), skip: int = 0, limit: int = 50):
    statement = select(Review).where(Review.user_id == user_id).offset(skip).limit(limit)
    results = session.exec(statement).all()
    return results
