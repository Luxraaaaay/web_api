import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False, expire_on_commit=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session