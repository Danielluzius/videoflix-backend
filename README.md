# Videoflix Backend

🌐 Language: English | [Deutsch](README.de.md)

A Netflix-like video streaming backend built with Django and Django REST Framework. Videos are automatically converted to HLS format (480p / 720p / 1080p) in the background using FFmpeg and Django RQ. Authentication is handled via JWT tokens stored in HTTP-only cookies.

This project was developed as part of the Developer Akademie curriculum.

---

## Quick Start with Docker

**Step 1 - Clone the repository and navigate into the backend folder:**

```bash
git clone https://github.com/Danielluzius/videoflix-backend.git
cd videoflix-backend/backend
```

**Step 2 - Copy the environment file:**

```bash
cp .env.example .env
```

**Step 3 - Fill in your values in `.env`** (minimum required):

```env
SECRET_KEY=your-secret-key
DB_NAME=videoflix
DB_USER=videoflix_user
DB_PASSWORD=yourpassword
EMAIL_HOST=smtp.your-provider.com
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=yourpassword
DEFAULT_FROM_EMAIL=you@example.com
FRONTEND_URL=http://127.0.0.1:5500
```

> **Note:** You need a working SMTP account to receive activation and password reset emails. Any provider works (Gmail, Outlook, etc.). For Gmail, use an [App Password](https://myaccount.google.com/apppasswords) with `smtp.gmail.com` on port `587`.

**Step 4 - Start all containers:**

```bash
docker compose up --build
```

> **No additional software required.** FFmpeg, PostgreSQL, and Redis are all included in the Docker setup.

**Step 5 - Start the frontend:**

Clone the [Videoflix frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix) and open it with a Live Server on port `5500` (e.g. the [VS Code Live Server extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)).
This is required for activation and password reset links to work correctly.

The API is available at `http://localhost:8000/api/`.
The admin panel is available at `http://localhost:8000/admin/` (login: `admin@example.com` / `adminpassword`).

---

## Tech Stack

| Technology            | Version | Purpose                                 |
| --------------------- | ------- | --------------------------------------- |
| Python                | 3.12    | Runtime                                 |
| Django                | 6.0.4   | Web framework                           |
| Django REST Framework | 3.17.1  | REST API                                |
| SimpleJWT             | 5.5.1   | JWT authentication                      |
| PostgreSQL            | 17+     | Primary database                        |
| Redis                 | latest  | Caching + message broker                |
| Django RQ             | 4.1.0   | Background task queue                   |
| Gunicorn              | 25.3.0  | WSGI production server                  |
| WhiteNoise            | 6.12.0  | Static file serving                     |
| FFmpeg                | 8.1     | Video conversion + thumbnail generation |
| Pillow                | 12.2.0  | Image field support                     |
| django-ratelimit      | 4.1.0   | Rate limiting on auth endpoints         |

---

## Project Structure

```
backend/
    core/                   # Django project configuration
        settings.py         # All settings (loaded from .env)
        urls.py             # Root URL configuration
    user_app/               # User authentication & account management
        api/
            views.py        # Register, Login, Logout, Password Reset
            serializers.py
            urls.py
        models.py           # CustomUser model (email-based auth)
        services.py         # Business logic for user operations
        tasks.py            # Background email tasks
        utils.py            # Email sending helpers
        authentication.py   # Custom JWT cookie authentication
    video_app/              # Video upload, processing & streaming
        api/
            views.py        # VideoList, VideoUpload, HLS playlist/segment views
            serializers.py
            urls.py
        models.py           # Video model
        tasks.py            # Background video processing task
        utils.py            # FFmpeg helpers (HLS conversion, thumbnail)
        signals.py          # post_save signal triggers processing
    templates/              # HTML email templates
    media/                  # Uploaded videos, HLS segments, thumbnails (gitignored)
    .env.example            # Template for environment variables
    requirements.txt        # Python dependencies
    backend.Dockerfile      # Docker image definition
    backend.entrypoint.sh   # Docker container startup script
    docker-compose.yml      # Docker service definitions
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values. To generate a secure `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable               | Example Value                                 | Description                                                            |
| ---------------------- | --------------------------------------------- | ---------------------------------------------------------------------- |
| `SECRET_KEY`           | `django-insecure-...`                         | Django secret key. Generate a new one for production.                  |
| `DEBUG`                | `True`                                        | Set to `False` in production.                                          |
| `ALLOWED_HOSTS`        | `localhost,127.0.0.1`                         | Comma-separated list of allowed hosts.                                 |
| `DB_NAME`              | `videoflix`                                   | PostgreSQL database name.                                              |
| `DB_USER`              | `videoflix_user`                              | PostgreSQL username.                                                   |
| `DB_PASSWORD`          | `yourpassword`                                | PostgreSQL password.                                                   |
| `DB_HOST`              | `localhost`                                   | PostgreSQL host. Use `db` inside Docker.                               |
| `DB_PORT`              | `5432`                                        | PostgreSQL port.                                                       |
| `REDIS_HOST`           | `localhost`                                   | Redis host. Use `redis` inside Docker.                                 |
| `REDIS_PORT`           | `6379`                                        | Redis port.                                                            |
| `REDIS_DB`             | `0`                                           | Redis database index for RQ.                                           |
| `REDIS_LOCATION`       | `redis://localhost:6379/1`                    | Full Redis URL for Django cache. Use `redis://redis:6379/1` in Docker. |
| `EMAIL_HOST`           | `smtp.your-provider.com`                      | SMTP server hostname.                                                  |
| `EMAIL_PORT`           | `587`                                         | SMTP port.                                                             |
| `EMAIL_HOST_USER`      | `you@example.com`                             | SMTP login username.                                                   |
| `EMAIL_HOST_PASSWORD`  | `yourpassword`                                | SMTP login password.                                                   |
| `EMAIL_USE_TLS`        | `True`                                        | Enable TLS for SMTP.                                                   |
| `DEFAULT_FROM_EMAIL`   | `you@example.com`                             | Sender address shown in emails.                                        |
| `FRONTEND_URL`         | `http://127.0.0.1:5500`                       | Base URL of the frontend. Used in activation and password reset links. |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:5500,http://127.0.0.1:5500` | Comma-separated trusted origins for CSRF and CORS.                     |

---

## API Endpoints

All endpoints are prefixed with `/api/`.

### Authentication

<details>
<summary>POST /api/register/ - Register a new user</summary>

Creates a new user account. The account is inactive until the activation link in the confirmation email is clicked.

**Rate limit:** 5 requests per minute per IP

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "confirmed_password": "securepassword"
}
```

**Responses:** `201` Created - `400` Validation error - `429` Rate limit exceeded

</details>

<details>
<summary>GET /api/activate/&lt;uidb64&gt;/&lt;token&gt;/ - Activate account</summary>

Activates a user account using the token from the confirmation email.

**Responses:** `200` Success - `400` Invalid or expired token

</details>

<details>
<summary>POST /api/login/ - Login</summary>

Authenticates the user and sets two HTTP-only cookies: `access_token` (20 min) and `refresh_token` (7 days).

**Rate limit:** 10 requests per minute per IP

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Responses:** `200` Sets `access_token` + `refresh_token` cookies - `401` Invalid credentials - `429` Rate limit exceeded

</details>

<details>
<summary>POST /api/logout/ - Logout</summary>

Blacklists the refresh token and deletes both cookies.

**Requires:** `refresh_token` cookie

**Responses:** `200` Success - `400` Refresh token missing

</details>

<details>
<summary>POST /api/token/refresh/ - Refresh access token</summary>

Issues a new `access_token` cookie using the existing `refresh_token` cookie.

**Requires:** `refresh_token` cookie

**Responses:** `200` New `access_token` cookie set - `400` Token missing - `401` Invalid or expired

</details>

<details>
<summary>POST /api/password_reset/ - Request password reset</summary>

Sends a password reset email. The response is always identical regardless of whether the email exists (security).

**Rate limit:** 5 requests per minute per IP

**Request body:**

```json
{
  "email": "user@example.com"
}
```

**Responses:** `200` Email sent (always)

</details>

<details>
<summary>POST /api/password_confirm/&lt;uidb64&gt;/&lt;token&gt;/ - Confirm new password</summary>

Sets the new password using the token from the password reset email.

**Request body:**

```json
{
  "new_password": "newsecurepassword",
  "confirm_password": "newsecurepassword"
}
```

**Responses:** `200` Success - `400` Invalid or expired token

</details>

### Videos

<details>
<summary>GET /api/video/ - List all videos</summary>

Returns all fully processed videos (HLS conversion complete), ordered by creation date descending.

**Requires:** Authentication (access_token cookie)

**Responses:** `200` Video list - `401` Not authenticated

</details>

<details>
<summary>POST /api/video/upload/ - Upload a video (admin only)</summary>

Uploads a new video and queues it for background processing (HLS conversion + thumbnail via FFmpeg).

**Requires:** Admin authentication (`is_staff = True`)
**Content-Type:** `multipart/form-data`

| Field         | Type            | Required |
| ------------- | --------------- | -------- |
| `title`       | string          | yes      |
| `description` | string          | no       |
| `category`    | string (choice) | yes      |
| `video_file`  | file            | yes      |

**Responses:** `201` Upload queued - `400` Validation error - `403` Not admin

</details>

<details>
<summary>GET /api/video/&lt;video_id&gt;/&lt;resolution&gt;/index.m3u8 - HLS playlist</summary>

Returns the HLS playlist for a specific video and resolution (`480p`, `720p`, `1080p`).

**Requires:** Authentication (access_token cookie)

**Responses:** `200` Playlist file - `404` Not found

</details>

<details>
<summary>GET /api/video/&lt;video_id&gt;/&lt;resolution&gt;/&lt;segment&gt;/ - HLS segment</summary>

Returns a single `.ts` video segment for playback.

**Requires:** Authentication (access_token cookie)

**Responses:** `200` Binary segment - `404` Not found

</details>

---

## Background Tasks

Django RQ runs two types of background tasks:

**Email tasks** (`user_app/tasks.py`)

- `task_send_activation_email(user)` - sends account activation email after registration
- `task_send_password_reset_email(user)` - sends password reset email

**Video processing** (`video_app/tasks.py`)

- `process_video(video_id)` - triggered via `post_save` signal on new Video uploads
  1. Runs FFmpeg - produces 480p / 720p / 1080p HLS variants + `master.m3u8`
  2. Extracts thumbnail at the 3-second mark
  3. Saves paths on the Video model and sets `processing_done = True`

Only videos with `processing_done = True` are returned by the video list endpoint.

---

## Notes for Windows Users

RQ uses `os.fork()` internally, which is not available on Windows. Use `SimpleWorker` for local development:

```bash
python manage.py rqworker default --worker-class rq.SimpleWorker
```

This is handled automatically inside the Docker container (Linux).
