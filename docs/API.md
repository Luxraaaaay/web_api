# Game Stats & Recommendation API — Comprehensive API Documentation

Version: 1.0

## Overview & Test Method
- **Base URL**: `http://127.0.0.1:8000`
- **Authentication**: JWT Bearer tokens. Include `Authorization: Bearer <access_token>` in requests that require it.

**Testing via /docs (Swagger UI)**
The primary and recommended way to test this API is through the interactive OpenAPI documentation provided by FastAPI.
1. Open your browser and navigate to `http://127.0.0.1:8000/docs` (or `https://steam-games-stats-and-recommendation-api.onrender.com/docs`).
2. Create a user via `POST /auth/register`.
3. Call `POST /auth/login` to secure an `access_token`.
4. Click the **Authorize** lock button at the top right of the page and paste the exact token string (e.g., `eyJhbG...`), and click "Authorize".
5. For any endpoint, click "Try it out", fill in the Parameters/Request body as shown in the "Swagger UI Test Input" sections below, and click "Execute". The UI automatically generates the correct curl commands and displays proper responses.

## 1. Auth

### POST /auth/register
- **Description**: Create a new user.
- **Authentication**: None
- **Parameters**: 
  - `Body (JSON)`: `username` (string), `email` (string), `password` (string)
- **Swagger UI Test Input**: 
  - **Request body**: `{ "username": "alice", "email": "alice@example.com", "password": "secretpassword" }`
- **Terminal (Curl) Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/auth/register" \
       -H "Content-Type: application/json" \
       -d '{"username":"alice","email":"alice@example.com","password":"secretpassword"}'
  ```
- **Expected Response (201 Created)**:
  ```json
  { "id": 1, "username": "alice", "email": "alice@example.com", "role": "player" }
  ```
- **Error Codes**: `400 Bad Request` (validation error or duplicate user).

### POST /auth/login
- **Description**: Login to receive a JWT access token.
- **Authentication**: None
- **Parameters**:
  - `Body (JSON)`: `username` (string), `password` (string)
- **Swagger UI Test Input**:
  - **Request body**: `{ "username": "alice", "password": "secretpassword" }`
- **Terminal (Curl) Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/auth/login" \
       -H "Content-Type: application/json" \
       -d '{"username":"alice","password":"secretpassword"}'
  ```
- **Expected Response (200 OK)**:
  ```json
  { "access_token": "eyJhbGciOi...", "token_type": "bearer" }
  ```
- **Error Codes**: `401 Unauthorized` (Incorrect username/password).

## 2. Users

### GET /users/me
- **Description**: Return current authenticated user's profile.
- **Authentication**: Required
- **Parameters**: None
- **Swagger UI Test Input**: 
  - Ensure Authorization header is active via clicking the lock icon.
  - Click "Execute".
- **Terminal (Curl) Example**:
  ```bash
  curl -X GET "http://127.0.0.1:8000/users/me" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (200 OK)**:
  ```json
  { "id": 1, "username": "alice", "email": "alice@example.com", "role": "player", "created_at": "2026-04-17T12:00:00Z" }
  ```
- **Error Codes**: `401 Unauthorized` (missing/invalid token).

### PATCH /users/me
- **Description**: Update current user's email or bio.
- **Authentication**: Required
- **Parameters**:
  - `Body (JSON)`: `email` (string, optional), `password` (string, optional)
- **Swagger UI Test Input**:
  - **Request body**: `{ "email": "newalice@example.com" }`
- **Terminal (Curl) Example**:
  ```bash
  curl -X PATCH "http://127.0.0.1:8000/users/me" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"email":"newalice@example.com"}'
  ```
- **Expected Response (200 OK)**: Updated user object.
- **Error Codes**: `400 Bad Request`, `401 Unauthorized`.

### GET /users/{user_id}
- **Description**: Get user profile by ID.
- **Authentication**: None
- **Parameters**: `user_id` (Path parameter, integer)
- **Swagger UI Test Input**:
  - **user_id**: `1`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/users/1"
  ```
- **Expected Response (200 OK)**: User profile JSON.
- **Error Codes**: `404 Not Found`.

### GET /users/{user_id}/favorites
- **Description**: Get a user's favorites (paginated).
- **Authentication**: None
- **Parameters**: 
  - `user_id` (Path, integer)
  - `skip` (Query, integer, default 0)
  - `limit` (Query, integer, default 50)
- **Swagger UI Test Input**: 
  - **user_id**: `1`
  - **skip**: `0`
  - **limit**: `10`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/users/1/favorites?limit=10&skip=0"
  ```
- **Expected Response (200 OK)**: `[ { "id": 7, "user_id": 1, "game_id": 2, "created_at": "..." } ]`

### GET /users/{user_id}/reviews
- **Description**: Get a user's reviews (paginated).
- **Authentication**: None
- **Parameters**:
  - `user_id` (Path, integer)
  - `skip` (Query, default 0)
  - `limit` (Query, default 50)
- **Swagger UI Test Input**: 
  - **user_id**: `1`
  - **limit**: `10`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/users/1/reviews?limit=10&skip=0"
  ```
- **Expected Response (200 OK)**: `[ { "id": 10, "rating": 5, "content": "Loved it!", "game_id": 1 } ]`

## 3. Games

### GET /games/
- **Description**: List games with search, filters, sorting, and pagination.
- **Authentication**: None
- **Parameters**: 
  - `q` (Query, string - search keyword)
  - `skip` (Query, integer, default 0)
  - `limit` (Query, integer, default 20)
- **Swagger UI Test Input**: 
  - **q**: `space`
  - **limit**: `5`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/games/?q=space&limit=5&skip=0"
  ```
- **Expected Response (200 OK)**: Paginated matching game objects JSON array.

### POST /games/
- **Description**: Create a new game.
- **Authentication**: Required (Admin/Publisher recommended)
- **Parameters**: 
  - `Body (JSON)`: containing game schema (title, steam_appid, description, etc.)
- **Swagger UI Test Input**: 
  - **Request body**: `{ "title": "Epic Journey", "steam_appid": 99999, "description": "Fun game", "is_released": true }`
- **Terminal (Curl) Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/games/" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"title":"Epic Journey","steam_appid":99999,"description":"Fun game"}'
  ```
- **Expected Response (201 Created)**: JSON of created Game object.

### GET /games/{game_id}
- **Description**: Retrieve game details by ID.
- **Authentication**: None
- **Parameters**: `game_id` (Path, integer)
- **Swagger UI Test Input**: 
  - **game_id**: `1`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/games/1"
  ```
- **Expected Response (200 OK)**: Game metadata.
- **Error Codes**: `404 Not Found`.

### PATCH /games/{game_id}
- **Description**: Partially update game info.
- **Authentication**: Required
- **Parameters**: 
  - `game_id` (Path, integer)
  - `Body (JSON)` with updated fields.
- **Swagger UI Test Input**: 
  - **game_id**: `1`
  - **Request body**: `{ "title": "Updated Journey Title" }`
- **Terminal (Curl) Example**:
  ```bash
  curl -X PATCH "http://127.0.0.1:8000/games/1" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"title":"Updated Journey Title"}'
  ```
- **Expected Response (200 OK)**: Updated game object.

### DELETE /games/{game_id}
- **Description**: Delete a game.
- **Authentication**: Required
- **Parameters**: `game_id` (Path, integer)
- **Swagger UI Test Input**: `game_id`: `1`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X DELETE "http://127.0.0.1:8000/games/1" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (204 No Content)**.

### GET /games/{game_id}/reviews
- **Description**: List reviews assigned to a game.
- **Authentication**: None
- **Parameters**: 
  - `game_id` (Path, integer)
  - `limit` (Query)
  - `skip` (Query)
- **Swagger UI Test Input**: `game_id`: `1`, `limit`: `20`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/games/1/reviews?limit=20&skip=0"
  ```
- **Expected Response (200 OK)**: JSON array of Reviews in items.

### POST /games/{game_id}/assets
- **Description**: Upload asset files (images/videos) for a game.
- **Authentication**: Required
- **Parameters**: 
  - `game_id` (Path, integer)
  - `files` (FormData/File)
- **Swagger UI Test Input**: 
  - **game_id**: `1`
  - **files**: [Select an image file using browser dialogue]
- **Terminal (Curl) Example**: 
  ```bash
  curl -X POST "http://127.0.0.1:8000/games/1/assets" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
       -F "files=@screenshot.png"
  ```

### GET /games/publishers/{publisher_id}/games
- **Description**: List games by developer/publisher ID.
- **Authentication**: None
- **Parameters**: `publisher_id` (Path, integer)
- **Swagger UI Test Input**: `publisher_id`: `5`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/games/publishers/5/games"
  ```

## 4. Reviews

### GET /reviews/games/{game_id}/reviews
- **Description**: Alias route to get reviews for a specific game.
- **Authentication**: None
- **Parameters**: `game_id` (Path)
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/reviews/games/1/reviews"
  ```

### POST /reviews/games/{game_id}/reviews
- **Description**: Submit a review for a game.
- **Authentication**: Required
- **Parameters**: 
  - `game_id` (Path, integer)
  - `Body (JSON)`: `rating` (integer 1-5), `content` (string)
- **Swagger UI Test Input**: 
  - **game_id**: `1`
  - **Request body**: `{ "rating": 5, "content": "Masterpiece!" }`
- **Terminal (Curl) Example**:
  ```bash
  curl -X POST "http://127.0.0.1:8000/reviews/games/1/reviews" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"rating":5,"content":"Masterpiece!"}'
  ```
- **Expected Response (201 Created)**: Output JSON for the created review.

### POST /reviews/{review_id}/like
- **Description**: Like an existing review.
- **Authentication**: Required
- **Parameters**: `review_id` (Path, integer)
- **Swagger UI Test Input**: `review_id`: `10`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X POST "http://127.0.0.1:8000/reviews/10/like" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (201 Created)**: `{ "id": 1, "review_id": 10 }`

### DELETE /reviews/{review_id}
- **Description**: Delete a review.
- **Authentication**: Required
- **Parameters**: `review_id` (Path, integer)
- **Terminal (Curl) Example**: 
  ```bash
  curl -X DELETE "http://127.0.0.1:8000/reviews/10" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (204 No Content)**

## 5. Favorites

### GET /favorites/users/me
- **Description**: List current user's favorite games.
- **Authentication**: Required
- **Parameters**: None
- **Swagger UI Test Input**: Ensure Authorization is complete, click Execute.
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/favorites/users/me" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (200 OK)**: `[ { "id": 5, "user_id": 1, "game_id": 2 } ]`

### POST /favorites/games/{game_id}/favorite
- **Description**: Add a game to current user's favorites.
- **Authentication**: Required
- **Parameters**: `game_id` (Path, integer)
- **Swagger UI Test Input**: `game_id`: `2`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X POST "http://127.0.0.1:8000/favorites/games/2/favorite" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (201 Created)**: Favorite mapping object.

### DELETE /favorites/games/{game_id}/favorite
- **Description**: Remove a game from favorites.
- **Authentication**: Required
- **Parameters**: `game_id` (Path, integer)
- **Terminal (Curl) Example**: 
  ```bash
  curl -X DELETE "http://127.0.0.1:8000/favorites/games/2/favorite" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```
- **Expected Response (204 No Content)**

## 6. Search

### GET /search/
- **Description**: Comprehensive search across games.
- **Authentication**: None
- **Parameters**: `q` (Query, string)
- **Swagger UI Test Input**: **q**: `battle`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/search/?q=battle"
  ```
- **Expected Response (200 OK)**: List of search results JSON.

### GET /search/suggestions
- **Description**: Autocomplete search suggestions.
- **Authentication**: None
- **Parameters**: `q` (Query, string)
- **Swagger UI Test Input**: **q**: `bat`
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/search/suggestions?q=bat"
  ```

## 7. Recommendations

### GET /recommendations/popular
- **Description**: Get popular or trending game recommendations.
- **Authentication**: None
- **Parameters**: None
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/recommendations/popular"
  ```

### GET /recommendations/personal
- **Description**: Get personalized game recommendations based on the user's reviews and favorites.
- **Authentication**: Required
- **Parameters**: None
- **Swagger UI Test Input**: Click Execute after Authorizing.
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/recommendations/personal" \
       -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
  ```

## 8. Health & Docs

### GET /health
- **Description**: Service health check endpoint.
- **Authentication**: None
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/health"
  ```
- **Expected Response**: `{"status": "ok"}`

### GET /openapi.json
- **Description**: Raw OpenAPI spec for programmatic integration.
- **Terminal (Curl) Example**: 
  ```bash
  curl -X GET "http://127.0.0.1:8000/openapi.json"
  ```

### GET /docs
- **Description**: Swagger UI for interactive browser testing. (No curl available).

---
## Error Codes Overview
- `400 Bad Request`: Invalid parameters or duplicate entry.
- `401 Unauthorized`: Token missing, invalid, or expired.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Specific resource not found.
- `422 Unprocessable Entity`: Built-in FastAPI body/query validation error.
- `500 Internal Server Error`: Server exception.

