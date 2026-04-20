# Game Stats & Recommendation API — API Documentation

Version: 1.0

Overview
- Base URL: depends on runtime host, e.g. `http://127.0.0.1:8000`.
- Authentication: JWT Bearer tokens. Include `Authorization: Bearer <access_token>` in requests that require authentication.

Error format
- Errors are returned as JSON, for example `{ "detail": "error message" }` or `{ "code": "ERR_CODE", "detail": "explanation" }`.
- Common HTTP status codes:
  - `200 OK` successful response
  - `201 Created` resource created
  - `204 No Content` successful deletion or no content
  - `400 Bad Request` invalid request parameters
  - `401 Unauthorized` authentication required or token invalid
  - `403 Forbidden` insufficient permissions
  - `404 Not Found` resource not found
  - `429 Too Many Requests` rate limited
  - `500 Internal Server Error` server error

Authentication flow (example)
1. Call `POST /auth/login` with `{ "username": "user", "password": "..." }`.
2. Receive `{ "access_token": "...", "token_type": "bearer" }` in response.
3. Include `Authorization: Bearer <access_token>` in subsequent requests.

------------------------------

## Auth

POST /auth/register
- Description: Register a new user
- Request example:

```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secret"
}
```
- Success: `201 Created`

POST /auth/login
- Description: User login, returns JWT
- Request example:

```json
{
  "username": "alice",
  "password": "secret"
}
```
- Success example:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```
 
Query examples

- Search + filters:

```bash
curl "http://127.0.0.1:8000/games?q=space+adventure&genre=Indie&platform=windows&min_rating=4&sort=avg_rating:desc&limit=10"
```

- Use `is_released=true` to restrict to released titles, or `is_released=false` for upcoming titles.

- `sort` supports `field` or `field:desc` for descending order (e.g. `release_date:desc`).

Notes

- When filtering by `min_rating`, the endpoint uses aggregated average ratings across reviews. If no ratings exist the game may be excluded depending on the query semantics.

POST /auth/refresh (optional)
- Description: Refresh access token using a refresh token (if implemented).

------------------------------

## Users

GET /users/{user_id}
- Description: Get public user profile
- Response example:

```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "role": "player",
  "created_at": "2026-04-17T12:00:00Z"
}
```

GET /users/me
- Description: Get the current authenticated user's full profile (auth required)

- Note: This endpoint requires a valid `Authorization: Bearer <access_token>` header. The `/users/me` route is intentionally ordered before `GET /users/{user_id}` to avoid path conflicts.

PATCH /users/me
- Description: Update current user (auth required)
- Request example (partial):

```json
{
  "email": "new@example.com",
  "bio": "I love indie games"
}
```

GET /users/{user_id}/favorites
- Description: Get user's favorites (paginated)

GET /users/{user_id}/reviews
- Description: Get user's reviews (paginated)

------------------------------

## Games

GET /games
- Description: List games. Supported query params:
  - `q` search keywords (title/description)
  - `genre` filter by genre
  - `platform` filter by platform
  - `is_released` boolean
  - `min_rating` minimum average rating
  - `sort` e.g. `release_date`, `avg_rating`, `popularity` (append `:desc` for descending)
  - `limit`/`offset` or `cursor`
- Response example (paginated):

```json
{
  "total": 12345,
  "items": [
    { "id": 1, "title": "My Game", "steam_appid": 123, "avg_rating": 4.2 },
    { "id": 2, "title": "Other Game", "steam_appid": 456, "avg_rating": 3.8 }
  ]
}
```

GET /games/{game_id}
- Description: Game details (includes aggregated rating and top reviews)
- Response example:

```json
{
  "id": 1,
  "title": "My Game",
  "steam_appid": 123,
  "developers": ["Dev Studio"],
  "publishers": ["Pub Co"],
  "genres": ["Action"],
  "platforms": ["windows"],
  "release_date": "2024-11-12T00:00:00Z",
  "avg_rating": 4.2,
  "top_reviews": [ { "id": 10, "rating": 5, "content": "Great" } ]
}
```

POST /games
- Description: Create a new game (publisher/dev/admin required)
- Request example:

```json
{
  "title": "New Game",
  "steam_appid": 999999,
  "developers": ["Dev"],
  "publishers": ["Pub"],
  "genres": ["Indie"],
  "platforms": ["windows", "mac"],
  "description": "Short description",
  "release_date": "2026-06-01T00:00:00Z"
}
```
- Success: `201 Created` with created resource.

PATCH /games/{game_id}
- Description: Update game info (publisher or admin)

DELETE /games/{game_id}
- Description: Delete or unpublish a game (publisher or admin), returns `204 No Content`.

POST /games/bulk-import (admin)
- Description: Upload and trigger a background import job; returns task id.

------------------------------

## Search

GET /search
- Description: Full-text or fielded search. Params: `q`, `filters`, `limit`, `offset`.

GET /search/suggestions
- Description: Search suggestions/autocomplete. Params: `q`, `limit`.

Optional: GET /search/semantic (vector semantic search if embeddings/vector store integrated).

------------------------------

## Reviews

GET /games/{game_id}/reviews
- Description: List reviews for a game (paginated, sortable)

POST /games/{game_id}/reviews
- Description: Submit a review (auth required)
- Request example:

```json
{
  "rating": 5,
  "content": "Really enjoyed this game!"
}
```

PATCH /reviews/{review_id}
- Description: Update a review (author or admin)

DELETE /reviews/{review_id}
- Description: Delete a review (author or admin)

POST /reviews/{review_id}/like
- Description: Like a review (auth required)

------------------------------

## Favorites

POST /games/{game_id}/favorite
- Description: Add favorite (auth required), returns `201`.

DELETE /games/{game_id}/favorite
- Description: Remove favorite (auth required), returns `204`.

GET /users/me/favorites
- Description: Get current user's favorites (auth required, paginated)

------------------------------

## Publisher / Admin features

GET /publishers/{publisher_id}/games
- Description: List games published by a publisher

POST /admin/import-csv
- Description: Upload CSV and trigger async import (admin required)

GET /tasks/{task_id}
- Description: Query async task status (import/embedding tasks)

Admin sample endpoints
- GET /admin/users
- PATCH /admin/users/{id}/role
- POST /admin/ban-user

------------------------------

## Media & Assets

POST /games/{game_id}/assets
- Description: Upload images/videos or request presigned URL (auth/publisher required)

------------------------------

## Recommendations

GET /recommendations/personal
- Description: Personalized recommendations based on user behavior (auth required)

GET /recommendations/popular
- Description: Return popular/trending recommendations

POST /recommendations/retrain (admin)
- Description: Trigger model retrain or rebuild indexes

------------------------------

## Health & Docs

GET /health
- Description: Health check, returns `{ "status": "ok" }`.

GET /openapi.json
- Description: OpenAPI spec (auto-generated by FastAPI).

GET /docs
- Description: Swagger UI (auto-provided by FastAPI).

------------------------------

Example error responses

400 Bad Request:
```json
{ "detail": "Invalid value for 'rating', must be 1-5" }
```

401 Unauthorized:
```json
{ "detail": "Not authenticated" }
```

403 Forbidden:
```json
{ "detail": "Insufficient permissions" }
```

404 Not Found:
```json
{ "detail": "Game not found" }
```

------------------------------
-
## Seed script
- Description: Import initial game data and optional sample users/favorites/reviews from a CSV file. The repository includes `scripts/seed.py` which by default reads `data/steam_games.csv`.

Usage (local):

```bash
python scripts/seed.py --file data/steam_games.csv --limit 200 --skip-existing
```

- The script creates hashed passwords for sample users, skips duplicates by default when `--skip-existing` is provided, and prints a short summary after import.

Convert to PDF
- We recommend using `pandoc` or printing to PDF from an editor (VS Code).

```bash
pandoc docs/API.md -o docs/API.pdf --from markdown
```

Windows PowerShell example:

```powershell
pandoc docs\API.md -o docs\API.pdf
```

Maintenance notes
- Add the generated `docs/API.pdf` to the repository and reference it in `README.md`.
