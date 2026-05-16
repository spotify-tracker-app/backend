# Backend API

A Django REST API that integrates with the Spotify Web API to provide user listening statistics and account information. Built with token-based authentication to securely link app users with their Spotify accounts.

---

## Features

- **Spotify OAuth2 Authentication** — redirect users to Spotify login and exchange the authorization code for tokens
- **Token Management** — automatic access token refresh using stored refresh tokens
- **Listening Stats** — fetch top tracks and artists across different time ranges
- **Recently Played** — retrieve the user's last 10 played tracks
- **Account Info** — access Spotify profile data

---

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL
- **External API:** Spotify Web API
- **Auth:** Token-based (app token passed via `Authorization` header)

---

## Project Structure

```
app/                    # Django project settings
├── settings.py
├── urls.py
├── asgi.py
└── wsgi.py

spotify_auth/           # Handles Spotify OAuth flow and token storage
├── models.py           # Token model
├── views.py            # Auth endpoints
├── extras.py           # Token helpers (create, refresh, validate)
├── credentials.py      # Env-based credentials loader
└── urls.py

stats/                  # Spotify data endpoints
├── views.py            # LastPlayed, PlayedStats, AccountInfo
└── urls.py
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- A [Spotify Developer App](https://developer.spotify.com/dashboard) with a registered redirect URI

### Installation

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root (or set these in your environment):

```env
SECRET_KEY=your_django_secret_key

CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
CLIENT_URI=your_spotify_redirect_uri

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Database Setup

```bash
python manage.py migrate
```

### Run the Server

```bash
python manage.py runserver
```

---

## API Reference

All endpoints require an app-level token passed in the `Authorization` header:

```
Authorization: Token <your_app_token>
```

---

### Auth Endpoints — `/auth/`

#### `GET /auth/login/`
Returns a Spotify OAuth authorization URL. Redirect the user to this URL to begin the login flow.

**Response:**
```json
{
  "url": "https://accounts.spotify.com/authorize?..."
}
```

---

#### `POST /auth/callback/`
Exchanges the Spotify authorization code for access and refresh tokens, and stores them linked to the app token.

**Request body:**
```json
{
  "code": "spotify_auth_code"
}
```

**Response:**
```json
{
  "Success": "Tokens stored successfully"
}
```

---

#### `GET /auth/is-authenticated/`
Checks whether the current app token has a valid Spotify session.

**Response:**
```json
{
  "status": true
}
```

---

#### `GET /auth/me/`
Returns the Spotify profile of the authenticated user.

---

#### `POST /auth/logout/`
Deletes stored Spotify tokens for the current app token.

**Response:**
```json
{
  "Success": "User logged out successfully"
}
```

---

### Stats Endpoints — `/stats/`

#### `GET /stats/last-played/`
Returns the 10 most recently played tracks.

---

#### `GET /stats/top-stats/?time_range=<range>`
Returns the user's top 10 tracks and top 10 artists for the given time range.

| `time_range` | Description |
|---|---|
| `short_term` | Last ~4 weeks (default) |
| `medium_term` | Last ~6 months |
| `long_term` | All time |

**Response:**
```json
{
  "time_range": "short_term",
  "top_tracks": [...],
  "top_artists": [...]
}
```

---

#### `GET /stats/account-info/`
Returns the authenticated user's Spotify account details.

---

## How Authentication Works

1. The frontend generates or holds an app-level token (e.g. a DRF auth token).
2. The token is passed on every request as `Authorization: Token <token>`.
3. On `/auth/callback/`, the Spotify OAuth code is exchanged and the resulting Spotify tokens are stored in the database, keyed to that app token.
4. On subsequent requests, the app token is used to look up the stored Spotify access token.
5. If the access token is expired, it is automatically refreshed using the stored refresh token.

---

## License

MIT
