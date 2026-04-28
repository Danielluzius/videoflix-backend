# Videoflix Backend

🌐 Sprache: [English](README.md) | Deutsch

Ein Netflix-ähnliches Video-Streaming-Backend, gebaut mit Django und Django REST Framework. Videos werden im Hintergrund automatisch ins HLS-Format (480p / 720p / 1080p) konvertiert – mit FFmpeg und Django RQ. Die Authentifizierung erfolgt über JWT-Tokens in HTTP-only Cookies.

Dieses Projekt wurde im Rahmen des Developer Akademie Lehrplans entwickelt.

---

## Quick Start mit Docker

**Schritt 1 - Umgebungsdatei kopieren:**

```bash
cp .env.example .env
```

**Schritt 2 - Werte in `.env` eintragen** (mindestens erforderlich):

```env
SECRET_KEY=dein-secret-key
DB_NAME=videoflix
DB_USER=videoflix_user
DB_PASSWORD=deinpasswort
EMAIL_HOST=smtp.dein-anbieter.com
EMAIL_HOST_USER=du@beispiel.de
EMAIL_HOST_PASSWORD=deinpasswort
DEFAULT_FROM_EMAIL=du@beispiel.de
FRONTEND_URL=http://127.0.0.1:5500
```

> **Hinweis:** Du benötigst einen funktionierenden SMTP-Account, um Aktivierungs- und Passwort-Reset-Mails zu empfangen. Jeder Anbieter funktioniert (Gmail, Outlook, etc.). Für Gmail: ein [App-Passwort](https://myaccount.google.com/apppasswords) mit `smtp.gmail.com` auf Port `587` verwenden.

**Schritt 3 - Alle Container starten:**

```bash
docker compose up --build
```

> **Keine zusätzliche Software erforderlich.** FFmpeg, PostgreSQL und Redis sind alle im Docker-Setup enthalten.

**Schritt 4 - Frontend starten:**

Das [Videoflix Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix) klonen und mit einem Live Server auf Port `5500` öffnen (z.B. die [VS Code Live Server Extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)).
Dies ist erforderlich, damit Aktivierungs- und Passwort-Reset-Links korrekt funktionieren.

Die API ist erreichbar unter `http://localhost:8000/api/`.
Das Admin-Panel ist erreichbar unter `http://localhost:8000/admin/` (Login: `admin@example.com` / `adminpassword`).

---

## Tech Stack

| Technologie           | Version | Zweck                                      |
| --------------------- | ------- | ------------------------------------------ |
| Python                | 3.12    | Laufzeitumgebung                           |
| Django                | 6.0.4   | Web-Framework                              |
| Django REST Framework | 3.17.1  | REST API                                   |
| SimpleJWT             | 5.5.1   | JWT-Authentifizierung                      |
| PostgreSQL            | 17+     | Primäre Datenbank                          |
| Redis                 | latest  | Caching + Message Broker                   |
| Django RQ             | 4.1.0   | Hintergrundaufgaben-Queue                  |
| Gunicorn              | 25.3.0  | WSGI-Produktionsserver                     |
| WhiteNoise            | 6.12.0  | Static-File-Serving                        |
| FFmpeg                | 8.1     | Videokonvertierung + Thumbnail-Generierung |
| Pillow                | 12.2.0  | Bildfeld-Unterstützung                     |
| django-ratelimit      | 4.1.0   | Rate Limiting auf Auth-Endpunkten          |

---

## Projektstruktur

```
backend/
    core/                   # Django-Projektkonfiguration
        settings.py         # Alle Einstellungen (aus .env geladen)
        urls.py             # Root-URL-Konfiguration
    user_app/               # Benutzerauthentifizierung & Kontoverwaltung
        api/
            views.py        # Register, Login, Logout, Passwort-Reset
            serializers.py
            urls.py
        models.py           # CustomUser-Modell (E-Mail-basierte Auth)
        services.py         # Business-Logik für Benutzeroperationen
        tasks.py            # Hintergrund-E-Mail-Tasks
        utils.py            # E-Mail-Helfer
        authentication.py   # Benutzerdefinierte JWT-Cookie-Authentifizierung
    video_app/              # Video-Upload, -Verarbeitung & -Streaming
        api/
            views.py        # VideoList, VideoUpload, HLS-Playlist/Segment-Views
            serializers.py
            urls.py
        models.py           # Video-Modell
        tasks.py            # Hintergrund-Videoverarbeitungs-Task
        utils.py            # FFmpeg-Helfer (HLS-Konvertierung, Thumbnail)
        signals.py          # post_save-Signal löst Verarbeitung aus
    templates/              # HTML-E-Mail-Templates
    media/                  # Hochgeladene Videos, HLS-Segmente, Thumbnails (gitignored)
    .env.example            # Vorlage für Umgebungsvariablen
    requirements.txt        # Python-Abhängigkeiten
    backend.Dockerfile      # Docker-Image-Definition
    backend.entrypoint.sh   # Docker-Container-Startskript
    docker-compose.yml      # Docker-Service-Definitionen
```

---

## Umgebungsvariablen

`.env.example` nach `.env` kopieren und Werte eintragen. So wird ein sicherer `SECRET_KEY` generiert:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

| Variable               | Beispielwert                                  | Beschreibung                                                                     |
| ---------------------- | --------------------------------------------- | -------------------------------------------------------------------------------- |
| `SECRET_KEY`           | `django-insecure-...`                         | Django Secret Key. Für Produktion neu generieren.                                |
| `DEBUG`                | `True`                                        | In Produktion auf `False` setzen.                                                |
| `ALLOWED_HOSTS`        | `localhost,127.0.0.1`                         | Kommagetrennte Liste erlaubter Hosts.                                            |
| `DB_NAME`              | `videoflix`                                   | PostgreSQL-Datenbankname.                                                        |
| `DB_USER`              | `videoflix_user`                              | PostgreSQL-Benutzername.                                                         |
| `DB_PASSWORD`          | `deinpasswort`                                | PostgreSQL-Passwort.                                                             |
| `DB_HOST`              | `localhost`                                   | PostgreSQL-Host. In Docker `db` verwenden.                                       |
| `DB_PORT`              | `5432`                                        | PostgreSQL-Port.                                                                 |
| `REDIS_HOST`           | `localhost`                                   | Redis-Host. In Docker `redis` verwenden.                                         |
| `REDIS_PORT`           | `6379`                                        | Redis-Port.                                                                      |
| `REDIS_DB`             | `0`                                           | Redis-Datenbankindex für RQ.                                                     |
| `REDIS_LOCATION`       | `redis://localhost:6379/1`                    | Vollständige Redis-URL für Django-Cache. In Docker `redis://redis:6379/1`.       |
| `EMAIL_HOST`           | `smtp.dein-anbieter.com`                      | SMTP-Server-Hostname.                                                            |
| `EMAIL_PORT`           | `587`                                         | SMTP-Port.                                                                       |
| `EMAIL_HOST_USER`      | `du@beispiel.de`                              | SMTP-Login-Benutzername.                                                         |
| `EMAIL_HOST_PASSWORD`  | `deinpasswort`                                | SMTP-Login-Passwort.                                                             |
| `EMAIL_USE_TLS`        | `True`                                        | TLS für SMTP aktivieren.                                                         |
| `DEFAULT_FROM_EMAIL`   | `du@beispiel.de`                              | Absenderadresse in E-Mails.                                                      |
| `FRONTEND_URL`         | `http://127.0.0.1:5500`                       | Basis-URL des Frontends. Wird in Aktivierungs- und Passwort-Reset-Links genutzt. |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:5500,http://127.0.0.1:5500` | Kommagetrennte vertrauenswürdige Origins für CSRF und CORS.                      |

---

## API-Endpunkte

Alle Endpunkte haben das Präfix `/api/`.

### Authentifizierung

<details>
<summary>POST /api/register/ - Neuen Benutzer registrieren</summary>

Erstellt ein neues Benutzerkonto. Das Konto ist inaktiv bis auf den Aktivierungslink in der Bestätigungsmail geklickt wird.

**Rate Limit:** 5 Anfragen pro Minute pro IP

**Request Body:**

```json
{
  "email": "benutzer@beispiel.de",
  "password": "sicherespasswort",
  "confirmed_password": "sicherespasswort"
}
```

**Antworten:** `201` Erstellt - `400` Validierungsfehler - `429` Rate Limit überschritten

</details>

<details>
<summary>GET /api/activate/&lt;uidb64&gt;/&lt;token&gt;/ - Konto aktivieren</summary>

Aktiviert ein Benutzerkonto mit dem Token aus der Bestätigungsmail.

**Antworten:** `200` Erfolg - `400` Ungültiger oder abgelaufener Token

</details>

<details>
<summary>POST /api/login/ - Einloggen</summary>

Authentifiziert den Benutzer und setzt zwei HTTP-only Cookies: `access_token` (20 Min.) und `refresh_token` (7 Tage).

**Rate Limit:** 10 Anfragen pro Minute pro IP

**Request Body:**

```json
{
  "email": "benutzer@beispiel.de",
  "password": "sicherespasswort"
}
```

**Antworten:** `200` Setzt `access_token` + `refresh_token` Cookies - `401` Ungültige Zugangsdaten - `429` Rate Limit überschritten

</details>

<details>
<summary>POST /api/logout/ - Ausloggen</summary>

Setzt den Refresh-Token auf die Blacklist und löscht beide Cookies.

**Erfordert:** `refresh_token` Cookie

**Antworten:** `200` Erfolg - `400` Refresh-Token fehlt

</details>

<details>
<summary>POST /api/token/refresh/ - Access-Token erneuern</summary>

Stellt einen neuen `access_token` Cookie mit dem vorhandenen `refresh_token` Cookie aus.

**Erfordert:** `refresh_token` Cookie

**Antworten:** `200` Neuer `access_token` Cookie gesetzt - `400` Token fehlt - `401` Ungültig oder abgelaufen

</details>

<details>
<summary>POST /api/password_reset/ - Passwort-Reset anfordern</summary>

Sendet eine Passwort-Reset-E-Mail. Die Antwort ist immer identisch, unabhängig davon ob die E-Mail existiert (Sicherheit).

**Rate Limit:** 5 Anfragen pro Minute pro IP

**Request Body:**

```json
{
  "email": "benutzer@beispiel.de"
}
```

**Antworten:** `200` E-Mail gesendet (immer)

</details>

<details>
<summary>POST /api/password_confirm/&lt;uidb64&gt;/&lt;token&gt;/ - Neues Passwort bestätigen</summary>

Setzt das neue Passwort mit dem Token aus der Passwort-Reset-E-Mail.

**Request Body:**

```json
{
  "new_password": "neuespasswort",
  "confirm_password": "neuespasswort"
}
```

**Antworten:** `200` Erfolg - `400` Ungültiger oder abgelaufener Token

</details>

### Videos

<details>
<summary>GET /api/video/ - Alle Videos auflisten</summary>

Gibt alle vollständig verarbeiteten Videos (HLS-Konvertierung abgeschlossen) zurück, nach Erstellungsdatum absteigend sortiert.

**Erfordert:** Authentifizierung (access_token Cookie)

**Antworten:** `200` Videoliste - `401` Nicht authentifiziert

</details>

<details>
<summary>POST /api/video/upload/ - Video hochladen (nur Admin)</summary>

Lädt ein neues Video hoch und stellt es zur Hintergrundverarbeitung in die Warteschlange (HLS-Konvertierung + Thumbnail via FFmpeg).

**Erfordert:** Admin-Authentifizierung (`is_staff = True`)
**Content-Type:** `multipart/form-data`

| Feld          | Typ             | Pflicht |
| ------------- | --------------- | ------- |
| `title`       | string          | ja      |
| `description` | string          | nein    |
| `category`    | string (choice) | ja      |
| `video_file`  | file            | ja      |

**Antworten:** `201` Upload in Warteschlange - `400` Validierungsfehler - `403` Kein Admin

</details>

<details>
<summary>GET /api/video/&lt;video_id&gt;/&lt;resolution&gt;/index.m3u8 - HLS-Playlist</summary>

Gibt die HLS-Playlist für ein bestimmtes Video und eine Auflösung (`480p`, `720p`, `1080p`) zurück.

**Erfordert:** Authentifizierung (access_token Cookie)

**Antworten:** `200` Playlist-Datei - `404` Nicht gefunden

</details>

<details>
<summary>GET /api/video/&lt;video_id&gt;/&lt;resolution&gt;/&lt;segment&gt;/ - HLS-Segment</summary>

Gibt ein einzelnes `.ts` Videosegment zur Wiedergabe zurück.

**Erfordert:** Authentifizierung (access_token Cookie)

**Antworten:** `200` Binäres Segment - `404` Nicht gefunden

</details>

---

## Hintergrundaufgaben

Django RQ führt zwei Arten von Hintergrundaufgaben aus:

**E-Mail-Tasks** (`user_app/tasks.py`)

- `task_send_activation_email(user)` - sendet Konto-Aktivierungsmail nach der Registrierung
- `task_send_password_reset_email(user)` - sendet Passwort-Reset-Mail

**Videoverarbeitung** (`video_app/tasks.py`)

- `process_video(video_id)` - ausgelöst via `post_save`-Signal bei neuen Video-Uploads
  1. Führt FFmpeg aus - erzeugt 480p / 720p / 1080p HLS-Varianten + `master.m3u8`
  2. Extrahiert Thumbnail bei der 3-Sekunden-Marke
  3. Speichert Pfade im Video-Modell und setzt `processing_done = True`

Nur Videos mit `processing_done = True` werden vom Video-Listen-Endpunkt zurückgegeben.

---

## Hinweise für Windows-Nutzer

RQ verwendet intern `os.fork()`, was unter Windows nicht verfügbar ist. Für lokale Entwicklung `SimpleWorker` verwenden:

```bash
python manage.py rqworker default --worker-class rq.SimpleWorker
```

Im Docker-Container (Linux) wird dies automatisch gehandhabt.
