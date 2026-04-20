# Steam Games Stats & Recommendation API
This project is a sample backend implemented with FastAPI and SQLModel. It provides endpoints for browsing Steam-like games, submitting reviews and favorites, uploading game assets, and simple recommendation/search endpoints. 

## Tech stack
- FastAPI — web framework
- SQLModel (built on SQLAlchemy) — ORM layer
- SQLite — built-in database backend used for simplicity (no external DB required)

## Key features
- User registration and login (JWT)
- Game listing with search, filters, sorting and pagination
- Game detail and publisher filtered listing
- Reviews: create, like, delete
- Favorites: add, remove, list
- File upload for game assets (multipart)
- Search suggestions and simple recommendations
- OpenAPI documentation available at `/docs`

## Requirements
- Python 3.9+

## Installation (Windows example)

1. Clone the repository and change into the project folder:

```powershell
git clone <repo-url>
cd web_api
```

2. (Optional) Create and activate a conda environment:

```powershell
conda create -n webapi python=3.10 -y
conda activate webapi
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Start the development server:

```powershell
uvicorn app.main:app --reload --port 8000
```

After the server starts, you can visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Healthcheck: `http://127.0.0.1:8000/health`

## Database note
This project uses `SQLModel` as the ORM and ships with an embedded SQLite backend for convenience. The repository does not include a checked-in `dev.db` file. When the application starts, if no `dev.db` file is present, the application will create the SQLite database file in the project root and initialize the required tables automatically.

## Using Swagger UI and obtaining a token
1. Use `POST /auth/register` to create a user (or `POST /auth/login` for an existing account).
2. Copy the `access_token` from the `POST /auth/login` response.
3. Click the **Authorize** button in the Swagger UI and paste the token into the `bearerAuth` input (only the raw token string, without the `Bearer ` prefix), then press Authorize.
4. Protected endpoints (for example `GET /users/me`) will now be called with the Authorization header.

CLI example (curl):

```bash
curl -X GET "http://127.0.0.1:8000/users/me" -H "Authorization: Bearer <TOKEN>"
```

## Example: create a game (requires authentication)
Request JSON example:

```json
{
  "steam_appid": 123456,
  "title": "Star Explorer",
  "developer_id": 2,
  "developers": ["StarDev Studios"],
  "publishers": ["Galactic Games"],
  "categories": ["Single-player", "Adventure"],
  "genres": ["Action", "Sci-fi"],
  "required_age": 12,
  "n_achievements": 42,
  "platforms": {"windows": true, "mac": true, "linux": false},
  "is_released": true,
  "description": "A space exploration action game with procedurally generated systems.",
  "release_date": "2024-11-15T00:00:00"
}
```

Curl example:

```bash
curl -X POST "http://127.0.0.1:8000/games/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '<PASTE_JSON_BODY>'
```

## Useful scripts
- `scripts/seed.py` — import CSV seed data (if present)

## Testing / usage hints for graders
- To initialize and run the API locally, running the `uvicorn` command above is sufficient; the server will create a local `dev.db` if needed.
- The repository intentionally does not include the database file or uploaded assets to keep the repo small and avoid exposing any test data.

## API Documentation PDF

PDF: [docs/API.pdf](docs/API.pdf)

---
