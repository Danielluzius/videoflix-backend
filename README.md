# Videoflix Backend

A Netflix-like video streaming backend built with Django and Django REST Framework. Videos are automatically converted to HLS format (480p / 720p / 1080p) in the background using FFmpeg and Django RQ. Authentication is handled via JWT tokens stored in HTTP-only cookies.

This project was developed as part of the Developer Akademie curriculum.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Local Development Setup](#local-development-setup)
- [Docker Setup](#docker-setup)
- [API Endpoints](#api-endpoints)
- [Background Tasks](#background-tasks)
- [Notes for Windows Users](#notes-for-windows-users)

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
| Docker                | latest  | Containerization                        |

---

## Prerequisites

<details>
<summary>Python 3.12</summary>

Download and install Python 3.12 from https://www.python.org/downloads/

Verify the installation:

```bash
python --version
# Python 3.12.x
```

</details>

<details>
<summary>PostgreSQL</summary>

Download and install PostgreSQL 17+ from https://www.postgresql.org/download/

After installation, create the database and user:

```sql
CREATE DATABASE videoflix;
CREATE USER videoflix_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE videoflix TO videoflix_user;
ALTER DATABASE videoflix OWNER TO videoflix_user;
```

Default connection settings (can be overridden via `.env`):

- Host: `localhost`
- Port: `5432`
- Database: `videoflix`
- User: `videoflix_user`

</details>

<details>
<summary>Redis</summary>

**Linux / macOS:**

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# macOS (Homebrew)
brew install redis
brew services start redis
```

**Windows:**

Redis does not officially support Windows. Use one of the following options:

- Install via WSL2 (Windows Subsystem for Linux) and run Redis inside WSL
- Use the community-maintained Windows port: https://github.com/tporadowski/redis/releases
- Run Redis in Docker (recommended): `docker run -d -p 6379:6379 redis:latest`

Verify Redis is running:

```bash
redis-cli ping
# PONG
```

</details>

<details>
<summary>FFmpeg</summary>

FFmpeg is required for video conversion (HLS) and thumbnail generation.

**Windows:**

1. Download a build from https://ffmpeg.org/download.html (e.g. gyan.dev builds)
2. Extract the archive
3. Add the `bin` folder to your system PATH environment variable
4. Verify: `ffmpeg -version`

**Linux / macOS:**

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

</details>

<details>
<summary>Docker (for Docker setup only)</summary>

Download and install Docker Desktop from https://www.docker.com/products/docker-desktop/

Docker Desktop includes both Docker Engine and Docker Compose.

Verify the installation:

```bash
docker --version
docker compose version
```

</details>

---

## Project Structure

```
backend/
    core/                   # Django project configuration
        settings.py         # All settings (loaded from .env)
        urls.py             # Root URL configuration
        wsgi.py
        asgi.py
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
        services.py         # Video query helpers
        tasks.py            # Background video processing task
        utils.py            # FFmpeg helpers (HLS conversion, thumbnail)
        signals.py          # post_save signal triggers processing
    templates/              # HTML email templates
    media/                  # Uploaded videos, HLS segments, thumbnails (gitignored)
    static/                 # Collected static files (gitignored)
    .env                    # Local environment variables (gitignored)
    .env.example            # Template for environment variables
    requirements.txt        # Python dependencies
    backend.Dockerfile      # Docker image definition
    backend.entrypoint.sh   # Docker container startup script
    docker-compose.yml      # Docker service definitions
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

<details>
<summary>All available variables</summary>

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
| `EMAIL_HOST`           | `smtp.ionos.de`                               | SMTP server hostname.                                                  |
| `EMAIL_PORT`           | `587`                                         | SMTP port.                                                             |
| `EMAIL_HOST_USER`      | `you@example.com`                             | SMTP login username.                                                   |
| `EMAIL_HOST_PASSWORD`  | `yourpassword`                                | SMTP login password.                                                   |
| `EMAIL_USE_TLS`        | `True`                                        | Enable TLS for SMTP.                                                   |
| `EMAIL_USE_SSL`        | `False`                                       | Enable SSL for SMTP (mutually exclusive with TLS).                     |
| `DEFAULT_FROM_EMAIL`   | `you@example.com`                             | Sender address shown in emails.                                        |
| `FRONTEND_URL`         | `http://127.0.0.1:5500`                       | Base URL of the frontend. Used in activation and password reset links. |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:5500,http://127.0.0.1:5500` | Comma-separated list of trusted origins for CSRF and CORS.             |

</details>

<details>
<summary>Generating a secure SECRET_KEY</summary>

Run this command to generate a new secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never commit your real `SECRET_KEY` to version control.

</details>

---

## Local Development Setup

<details>
<summary>Step 1 - Clone the repository</summary>

```bash
git clone <repository-url>
cd videoflix/backend
```

</details>

<details>
<summary>Step 2 - Create and activate a virtual environment</summary>

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux / macOS)
source .venv/bin/activate

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.\.venv\Scripts\activate.bat
```

</details>

<details>
<summary>Step 3 - Install dependencies</summary>

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary>Step 4 - Configure environment variables</summary>

```bash
cp .env.example .env
```

Open `.env` and fill in your PostgreSQL credentials, Redis host, email settings, and `FRONTEND_URL`.

For local development, the relevant values are:

```env
DB_HOST=localhost
REDIS_HOST=localhost
REDIS_LOCATION=redis://localhost:6379/1
```

</details>

<details>
<summary>Step 5 - Run database migrations</summary>

Make sure PostgreSQL is running and the database and user have been created (see Prerequisites).

```bash
python manage.py makemigrations
python manage.py migrate
```

</details>

<details>
<summary>Step 6 - Create a superuser</summary>

```bash
python manage.py createsuperuser
```

You will be prompted for an email address and password. This account can access the Django admin panel at `http://localhost:8000/admin/`.

</details>

<details>
<summary>Step 7 - Start the development server</summary>

```bash
python manage.py runserver
```

The API is now available at `http://localhost:8000/api/`.

</details>

<details>
<summary>Step 8 - Start the RQ worker (required for email and video processing)</summary>

The RQ worker processes background tasks such as sending activation emails and converting uploaded videos.

**Linux / macOS:**

```bash
python manage.py rqworker default
```

**Windows (required due to os.fork() limitation):**

```bash
python manage.py rqworker default --worker-class rq.SimpleWorker
```

The worker must be running whenever you upload a video or register a new user, otherwise tasks will stay queued and not execute.

</details>

---

## Docker Setup

The entire application (Django backend, PostgreSQL, Redis) can be started with a single Docker Compose command. This is the recommended way to run the project for submission.

<details>
<summary>Step 1 - Configure environment variables</summary>

```bash
cp .env.example .env
```

Open `.env` and fill in your values. The Docker Compose file overrides the host values automatically, so you do not need to change `DB_HOST` or `REDIS_HOST` in `.env` for Docker — they are set via the `environment` section in `docker-compose.yml`.

The following values must be set in `.env` for Docker to work correctly:

```env
SECRET_KEY=your-secret-key
DB_NAME=videoflix
DB_USER=videoflix_user
DB_PASSWORD=yourpassword
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=yourpassword
DEFAULT_FROM_EMAIL=you@example.com
FRONTEND_URL=http://127.0.0.1:5500
```

</details>

<details>
<summary>Step 2 - Build and start all containers</summary>

```bash
cd backend
docker compose up --build
```

This starts three containers:

| Container            | Service                       | Port     |
| -------------------- | ----------------------------- | -------- |
| `videoflix_backend`  | Django + Gunicorn + RQ Worker | `8000`   |
| `videoflix_database` | PostgreSQL 18                 | internal |
| `videoflix_redis`    | Redis                         | internal |

The entrypoint script automatically:

1. Waits for PostgreSQL to be ready
2. Runs `collectstatic`
3. Runs `makemigrations` and `migrate`
4. Creates the superuser (email: `admin@example.com`, password: `adminpassword`)
5. Starts the RQ worker
6. Starts Gunicorn on port 8000

The API is then available at `http://localhost:8000/api/`.
The Django admin panel is at `http://localhost:8000/admin/`.

</details>

<details>
<summary>Step 3 - Stop all containers</summary>

```bash
docker compose down
```

To also delete all volumes (database data, media files):

```bash
docker compose down -v
```

</details>

<details>
<summary>Rebuilding after code changes</summary>

If you change Python files while the containers are running, Gunicorn will reload automatically because of the `--reload` flag. If you change `requirements.txt` or the Dockerfile, you need to rebuild:

```bash
docker compose up --build
```

</details>

<details>
<summary>Viewing logs</summary>

```bash
# All services
docker compose logs -f

# Backend only
docker logs videoflix_backend -f

# Database only
docker logs videoflix_database -f
```

</details>

<details>
<summary>Running Django management commands inside Docker</summary>

```bash
# Open a shell inside the running backend container
docker exec -it videoflix_backend sh

# Run a management command
python manage.py shell
python manage.py createsuperuser
python manage.py migrate
```

</details>

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

**Success response (201):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com"
  },
  "token": "uid/activation-token"
}
```

**Error responses:**

- `400` - Validation error (e.g. email already in use, passwords do not match)
- `429` - Rate limit exceeded

</details>

<details>
<summary>GET /api/activate/&lt;uidb64&gt;/&lt;token&gt;/ - Activate account</summary>

Activates a user account using the token from the confirmation email. The frontend receives this link and forwards the parameters to this endpoint.

**Success response (200):**

```json
{
  "message": "Account successfully activated."
}
```

**Error responses:**

- `400` - Invalid or expired activation token

</details>

<details>
<summary>POST /api/login/ - Login</summary>

Authenticates the user and sets two HTTP-only cookies: `access_token` (20 minutes) and `refresh_token` (7 days).

**Rate limit:** 10 requests per minute per IP

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Success response (200):**

```json
{
  "detail": "Login successful",
  "user": {
    "id": 1,
    "username": "user@example.com"
  }
}
```

Sets cookies: `access_token`, `refresh_token` (both HTTP-only, SameSite=Lax)

**Error responses:**

- `401` - Invalid credentials or inactive account
- `429` - Rate limit exceeded

</details>

<details>
<summary>POST /api/logout/ - Logout</summary>

Blacklists the refresh token and deletes both cookies on the client.

**Requires:** `refresh_token` cookie

**Success response (200):**

```json
{
  "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."
}
```

**Error responses:**

- `400` - Refresh token cookie missing

</details>

<details>
<summary>POST /api/token/refresh/ - Refresh access token</summary>

Issues a new `access_token` cookie using the existing `refresh_token` cookie.

**Requires:** `refresh_token` cookie

**Success response (200):**

```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

Sets cookie: `access_token` (HTTP-only, SameSite=Lax)

**Error responses:**

- `400` - Refresh token missing
- `401` - Invalid or expired refresh token

</details>

<details>
<summary>POST /api/password_reset/ - Request password reset</summary>

Sends a password reset email to the given address. For security reasons, the response is always the same regardless of whether the email exists in the database.

**Rate limit:** 5 requests per minute per IP

**Request body:**

```json
{
  "email": "user@example.com"
}
```

**Success response (200):**

```json
{
  "detail": "An email has been sent to reset your password."
}
```

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

**Success response (200):**

```json
{
  "detail": "Your Password has been successfully reset."
}
```

**Error responses:**

- `400` - Invalid or expired token

</details>

### Videos

<details>
<summary>GET /api/video/ - List all videos</summary>

Returns all videos that have been fully processed (HLS conversion complete). Ordered by creation date descending.

**Requires:** Authentication (access_token cookie)

**Success response (200):**

```json
[
  {
    "id": 1,
    "title": "Movie Title",
    "description": "Movie description",
    "category": "Drama",
    "thumbnail_url": "http://localhost:8000/media/thumbnails/1.jpg",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

**Error responses:**

- `401` - Not authenticated

</details>

<details>
<summary>POST /api/video/upload/ - Upload a video (admin only)</summary>

Uploads a new video file. The video is saved and immediately queued for background processing (HLS conversion + thumbnail generation via FFmpeg).

**Requires:** Admin authentication (is_staff = True)

**Content-Type:** `multipart/form-data`

**Request fields:**

| Field         | Type            | Required |
| ------------- | --------------- | -------- |
| `title`       | string          | yes      |
| `description` | string          | no       |
| `category`    | string (choice) | yes      |
| `video_file`  | file            | yes      |

**Success response (201):**

```json
{
  "id": 1,
  "detail": "Upload successful. Video is being processed."
}
```

**Error responses:**

- `400` - Validation error
- `403` - Not an admin user

</details>

<details>
<summary>GET /api/video/&lt;video_id&gt;/&lt;resolution&gt;/index.m3u8 - HLS playlist</summary>

Returns the HLS playlist file for a specific video and resolution.

**Requires:** Authentication (access_token cookie)

**URL parameters:**

| Parameter    | Values                     |
| ------------ | -------------------------- |
| `video_id`   | Integer ID of the video    |
| `resolution` | `480p`, `720p`, or `1080p` |

**Success response (200):** HLS playlist file (`Content-Type: application/vnd.apple.mpegurl`)

**Error responses:**

- `404` - Video or playlist not found

</details>

<details>
<summary>GET /api/video/&lt;video_id&gt;/&lt;resolution&gt;/&lt;segment&gt;/ - HLS segment</summary>

Returns a single video segment file for playback.

**Requires:** Authentication (access_token cookie)

**URL parameters:**

| Parameter    | Example         |
| ------------ | --------------- |
| `video_id`   | `1`             |
| `resolution` | `720p`          |
| `segment`    | `segment000.ts` |

**Success response (200):** Binary video segment (`Content-Type: video/MP2T`)

**Error responses:**

- `404` - Segment not found

</details>

### Admin

<details>
<summary>Django Admin Panel</summary>

Available at `/admin/`. Log in with a superuser account.

From the admin panel you can:

- View and manage users (activate/deactivate accounts, change passwords)
- Upload and manage videos (the upload also triggers background processing)
- Monitor the processing status of videos (`processing_done` field)

</details>

---

## Background Tasks

The project uses Django RQ to run two types of background tasks:

<details>
<summary>Email tasks (user_app/tasks.py)</summary>

- `task_send_activation_email(user)` - Sends the account activation email after registration. Contains a link to activate the account.
- `task_send_password_reset_email(user)` - Sends the password reset email. Contains a link to set a new password.

Both tasks use Django's SMTP email backend. The email templates are located in `templates/`.

</details>

<details>
<summary>Video processing task (video_app/tasks.py)</summary>

- `process_video(video_id)` - Triggered automatically via a Django post_save signal whenever a new Video is uploaded.

What the task does:

1. Calls `convert_to_hls()` which runs FFmpeg to produce three quality levels (480p, 720p, 1080p) plus a master.m3u8 playlist
2. Calls `generate_thumbnail()` which extracts a still frame at the 3-second mark
3. Saves the HLS path and thumbnail path on the Video model
4. Sets `processing_done = True`

Only videos with `processing_done = True` are returned by the video list endpoint.

</details>

---

## Notes for Windows Users

<details>
<summary>RQ Worker on Windows</summary>

RQ uses `os.fork()` internally, which is not available on Windows. Running the default worker will crash with a `NotImplementedError`.

Use `SimpleWorker` instead:

```bash
python manage.py rqworker default --worker-class rq.SimpleWorker
```

This is handled automatically inside the Docker container (Linux), so this only applies to local development on Windows.

</details>

<details>
<summary>PowerShell execution policy</summary>

If activating the virtual environment fails in PowerShell with an error about script execution being disabled, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

</details>

<details>
<summary>FFmpeg not found</summary>

If Django or the RQ worker throws an error like `FileNotFoundError: [WinError 2] The system cannot find the file specified` when processing a video, FFmpeg is either not installed or not in your system PATH.

1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract and copy the `bin` folder path (e.g. `C:\ffmpeg\bin`)
3. Add that path to your Windows system environment variable `Path`
4. Restart your terminal
5. Verify: `ffmpeg -version`

</details>
