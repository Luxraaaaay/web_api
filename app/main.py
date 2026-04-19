from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.database import init_db
from app.routes import auth, games, reviews, favorites, users

app = FastAPI(title="Game Stats & Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(games.router, prefix="/games", tags=["games"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}