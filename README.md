# RetroNetwork

A modern, feature-rich social network application built with Django, Django REST Framework, and Django Channels for real-time WebSocket communication. Includes Cloudinary integration for reliable media storage and CDN delivery.

**[Quick Start](#quick-start)** • **[Features](#-features)** • **[Tech Stack](#tech-stack)** • **[Deployment](#deployment-to-rendercom)** • **[Security](#security-features)** • **[Troubleshooting](#troubleshooting)** • **[Docs](SECURITY.md)**

## ✨ Features

### Core Social Features
- **👥 User Profiles** — Customizable profiles with bio, avatar, cover image, and status
- **📝 Posts & Comments** — Create posts, comment, edit, and delete with rich text support
- **❤️ Reactions** — Like posts and comments
- **💬 Real-time Messaging** — WebSocket-based instant messaging with typing indicators and presence
- **📎 Media Handling** — Upload images, videos, and audio with Cloudinary CDN integration
- **🔔 Notifications** — Real-time notifications for follows, likes, comments, and messages

### Safety & Privacy
- **🔒 Privacy Controls** — Block/unblock users, followers/following management, privacy settings
- **🔐 Authentication** — Email, username, or handle login with custom backend
- **✅ File Validation** — Extension, MIME type, and file size validation for all uploads
- **🔐 Secure Sessions** — CSRF protection, secure cookies, HSTS headers

### User Experience
- **🔍 Search** — Full-text search for posts and users
- **🌓 Dark Theme** — Built-in light and dark theme support (localStorage preference)
- **📱 Responsive Design** — Mobile-friendly retro UI with modern functionality

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Django 6.0.2 | Web framework |
| **API** | Django REST Framework 3.16.1 | RESTful API endpoints |
| **Real-time** | Django Channels 4.3.2 | WebSocket messaging |
| **Database** | PostgreSQL 18 | Primary data storage |
| **Cache/Queue** | Redis 7 | Caching, sessions, Channels layer |
| **ASGI Server** | Daphne 4.2.1 | Async application server |
| **Web Server** | Gunicorn 25.1.0 | Production WSGI server |
| **Media Storage** | Cloudinary + CDN | Image/video/audio delivery |
| **Image Processing** | Pillow 12.1.0 | Thumbnail generation |
| **Static Files** | Whitenoise 6.12.0 | Efficient static file serving |

## Quick Start

### Local Development (with PostgreSQL & Redis)

1. **Clone and navigate**
   ```bash
   git clone https://github.com/Lolkov1ch/RetroNetwork.git
   cd RetroNetwork
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and configure:
   # - DATABASE_URL: PostgreSQL connection string
   # - REDIS_URL: Redis server location (optional, defaults to localhost)
   # - Cloudinary credentials (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```
   App available at `http://localhost:8000` — Admin at `http://localhost:8000/admin/`

### Local Development with Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/Lolkov1ch/RetroNetwork.git
   cd RetroNetwork
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services** (PostgreSQL, Redis, Django app)
   ```bash
   docker-compose up -d
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the app**
   - Application: `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin/`
   - Postgres: `localhost:5432` (user: `postgres`, password: `dev_password`)
   - Redis: `localhost:6379`

**Stop services:**
```bash
docker-compose down
```

## Deployment to Render.com

### Prerequisites
- Render.com account (free tier available)
- GitHub repository with code pushed
- PostgreSQL add-on on Render (recommended: paid tier for reliability)

### Deployment Steps

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Create Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `RetroNetwork`
   - Set environment to **Docker**
   - Choose a region (Frankfurt recommended for EU)
   - Select **Free** plan (or Paid for better performance)

3. **Create PostgreSQL Database** (if not using Render managed service)
   - New PostgreSQL instance on Render
   - Note the `DATABASE_URL`

4. **Add Environment Variables** in Render Web Service settings:
   ```
   SECRET_KEY                  = [auto-generated by Render]
   DEBUG                       = False
   ALLOWED_HOSTS               = your-service-name.onrender.com
   DATABASE_URL                = [your PostgreSQL connection string]
   REDIS_URL                   = [redis://:password@host:port]
   CLOUDINARY_CLOUD_NAME       = [your cloudinary cloud name]
   CLOUDINARY_API_KEY          = [your cloudinary api key]
   CLOUDINARY_API_SECRET       = [your cloudinary api secret]
   SECURE_SSL_REDIRECT         = True
   SESSION_COOKIE_SECURE       = True
   CSRF_COOKIE_SECURE          = True
   ```

5. **Deploy**
   - Render automatically builds from `Dockerfile.prod`
   - Migrations run automatically on startup
   - Service health checks enabled

6. **Post-Deployment**
   - Access your app: `https://your-service-name.onrender.com`
   - Check logs in Render dashboard if issues occur
   - Create superuser via Render shell:
     ```bash
     # In Render dashboard, open "Shell" and run:
     python manage.py createsuperuser
     ```

## Project Structure

```
RetroNetwork/
├── social_core/              # Main Django project settings
│   ├── settings.py          # Configuration (DB, apps, middleware, storage)
│   ├── storages.py          # Cloudinary storage classes
│   ├── asgi.py              # ASGI config for Channels
│   ├── wsgi.py              # WSGI config for Gunicorn
│   └── urls.py              # Main URL routing
│
├── users/                   # User authentication & profiles
│   ├── models.py            # User, Follow, Block models
│   ├── views.py             # Profile views
│   ├── backends.py          # Custom auth backend
│   └── forms.py             # User forms
│
├── posts/                   # Posts & content management
│   ├── models.py            # Post model
│   ├── views.py             # Post CRUD views
│   ├── signals.py           # Auto-update signals
│   └── utils.py             # Thumbnail generation
│
├── comments/                # Comments on posts
│   ├── models.py            # Comment model
│   ├── views.py             # Comment views
│   └── signals.py           # Notifications
│
├── reactions/               # Likes & reactions
│   ├── models.py            # Reaction model
│   └── views.py             # Reaction endpoints
│
├── messaging/               # WebSocket messaging
│   ├── consumers.py         # WebSocket consumer (Channels)
│   ├── models.py            # Message, Conversation models
│   ├── routing.py           # WebSocket routing
│   ├── serializers.py       # DRF serializers
│   └── views.py             # REST API views
│
├── notifications/           # Real-time notifications
│   ├── models.py            # Notification model
│   ├── signals.py           # Signal handlers
│   └── context_processors.py
│
├── attachments/             # File uploads & media storage
│   ├── models.py            # Media model (polymorphic attachment)
│   ├── validators.py        # File type, size, MIME validation
│   ├── storage_paths.py     # Upload path generation
│   └── migrations/          # Database migrations
│
├── user_settings/           # User preferences
│   ├── models.py            # Privacy, theme settings
│   └── views.py             # Settings views
│
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── social_network/      # Post/feed templates
│   ├── users/               # Profile templates
│   └── messenger/           # Messaging templates
│
├── static/                  # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── img/
│
├── Dockerfile               # Development image
├── Dockerfile.prod          # Production image (for Render)
├── docker-compose.yml       # Local dev orchestration
├── docker-compose.prod.yml  # Production orchestration
├── docker-entrypoint.sh     # Dev entrypoint
├── docker-entrypoint-prod.sh # Prod entrypoint (migrations, static)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── render.yaml              # Render deployment config
└── manage.py                # Django CLI
```

## Security Features

- **Custom Authentication** — Email, username, or handle login with custom backend
- **Password Validation** — Complexity checks, similarity validation, common password detection
- **File Upload Security**
  - ✅ Extension validation
  - ✅ MIME type verification
  - ✅ File size limits (25 MB images, 200 MB videos, 25 MB audio)
  - ✅ Image integrity checks (PIL verification)
  - ✅ Cloudinary CDN storage (no local file system exposure)
- **CORS Protection** — Configured allowed origins
- **CSRF Protection** — Enabled on all POST/PUT/DELETE operations
- **WebSocket Security** — Token-based authentication for real-time connections
- **SQL Injection Prevention** — Django ORM parameterized queries
- **XSS Prevention** — Django template auto-escaping
- **Container Security** — Runs as non-root user (UID 1000)
- **HTTPS/TLS** — HSTS headers, secure cookies configurable for production
- **Rate Limiting** — Configurable per-user and anonymous throttling

## Environment Variables

See `.env.example` for all available variables:

### Core Configuration
```bash
SECRET_KEY                      # Django secret key (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
DEBUG                           # Debug mode (True for dev, False for production)
ALLOWED_HOSTS                   # Comma-separated allowed domains
```

### Database & Cache
```bash
DATABASE_URL                    # PostgreSQL: postgresql://user:pass@host:port/dbname
REDIS_URL                       # Redis: redis://[:password@]host:port[/db]
CHANNEL_BACKEND                 # "channels.layers.InMemoryChannelLayer" or "channels_redis.core.RedisChannelLayer"
```

### Cloudinary Media Storage (Required for file uploads)
```bash
CLOUDINARY_CLOUD_NAME           # Your Cloudinary cloud name
CLOUDINARY_API_KEY              # Cloudinary API key
CLOUDINARY_API_SECRET           # Cloudinary API secret (keep secure!)
```

### Security Settings (Production)
```bash
SECURE_SSL_REDIRECT             # Enforce HTTPS (True for production)
SESSION_COOKIE_SECURE           # Secure session cookies
CSRF_COOKIE_SECURE              # Secure CSRF cookies
SECURE_HSTS_SECONDS             # HSTS header duration (31536000 = 1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS  # Include subdomains in HSTS
SECURE_HSTS_PRELOAD             # Allow preload in HSTS
```

## Development

### Cloudinary Setup
RetroNetwork uses Cloudinary for media storage and CDN delivery. For local development:

1. **Sign up** at [Cloudinary.com](https://cloudinary.com) (free tier available)
2. **Get credentials** from your Cloudinary dashboard:
   - Cloud Name
   - API Key
   - API Secret
3. **Add to `.env`:**
   ```bash
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

**Supported Media Types:**
- **Images**: .jpg, .jpeg, .png, .gif, .webp, .svg (25 MB max)
- **Videos**: .mp4, .webm, .avi, .mov, .mkv (200 MB max)
- **Audio**: .mp3, .wav, .m4a, .ogg, .webm, .aac (25 MB max)
- **Documents**: .pdf, .doc, .docx, .txt, .xlsx, .xls (50 MB max)

### Running Tests
```bash
python manage.py test
```

### Creating Test Data
```bash
python manage.py create_test_posts
python manage.py create_test_messages
```

### Collecting Static Files (local)
```bash
python manage.py collectstatic --noinput
```

## Database Migrations

Create new migration:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

## API Endpoints Overview

### Authentication
- `POST /api/auth/login/` — User login
- `POST /api/auth/logout/` — User logout
- `POST /api/auth/register/` — User registration

### Posts
- `GET /api/posts/` — List all posts
- `POST /api/posts/` — Create new post
- `GET /api/posts/{id}/` — Get post details
- `PUT /api/posts/{id}/` — Update post
- `DELETE /api/posts/{id}/` — Delete post

### Messages
- `GET /api/messages/conversations/` — List conversations
- `POST /api/messages/conversations/` — Create conversation
- `GET /api/messages/` — List messages
- `POST /api/messages/` — Send message (supports file uploads)

### WebSocket (Real-time)
- `wss://your-domain/ws/chat/{conversation_id}/` — Chat connection
- Automatically handles typing indicators, presence, and message delivery

### Complete API documentation available at `/api/docs/` when running Django REST Framework

## Troubleshooting

### File uploads failing
**Problem**: Upload button doesn't work or shows validation errors

**Solutions:**
1. Check Cloudinary credentials are set in `.env`
   ```bash
   python manage.py shell -c "from django.conf import settings; print(settings.CLOUDINARY_STORAGE)"
   ```
2. Verify file meets requirements (type, size)
3. Check browser console (F12) for JavaScript errors
4. Review Django logs: `tail -f logs/django.log`
5. Ensure storage is configured correctly:
   ```bash
   python manage.py shell -c "from social_core.storages import ImageCloudinaryStorage; print('Storage OK')"
   ```

### Build fails on Render
- Check that `DATABASE_URL` is set in environment variables
- Ensure the PostgreSQL database is running
- Verify Cloudinary credentials are configured
- Review logs in Render dashboard

### WebSocket connection fails
- Ensure Redis is available (set `REDIS_URL` for production)
- Check that `CHANNEL_BACKEND` is set correctly
- Verify firewall/network allows WebSocket connections

### Static files not serving
- Run `python manage.py collectstatic`
- Ensure Whitenoise is configured in settings
- Check file permissions in container

### Migration timeout
- Increase the `timeout` in docker-entrypoint-prod.sh
- Check database performance and connection

### Django system check errors
```bash
python manage.py check --deploy
```
Verify all settings are correct and no critical errors are reported.

## License

MIT License — See [LICENSE](LICENSE) file

**For more info:** See [SECURITY.md](SECURITY.md) for deployment and security best practices
