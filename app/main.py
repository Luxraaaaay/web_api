from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.database import init_db
from app.routes import auth, games, reviews, favorites, users
from app.routes import search, recommendations

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
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="Game Stats & Recommendation API",
        routes=app.routes,
    )

    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    # Add a Bearer JWT scheme so Swagger UI shows a raw token input
    security_schemes["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi