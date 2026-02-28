# RetroNetwork Security & Deployment Guide

## Overview
This document outlines security best practices and deployment guidelines for RetroNetwork.

## Environment Setup

### Development Environment
1. Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```

2. Generate a secure SECRET_KEY:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. Update `.env` with your SECRET_KEY and other settings

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Production Environment
1. **Create a production `.env` file with:**
   - `SECRET_KEY`: Generated random key (see above)
   - `DEBUG=False`: Always disable debug mode
   - `ALLOWED_HOSTS`: Your production domain(s)
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_HOST` and `REDIS_PORT`: Redis server details
   - `SECURE_SSL_REDIRECT=True`
   - `SESSION_COOKIE_SECURE=True`
   - `CSRF_COOKIE_SECURE=True`
   - `SECURE_HSTS_SECONDS=31536000` (1 year)
   - `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
   - `SECURE_HSTS_PRELOAD=True`

2. Never commit `.env` file to version control

## Security Features

### 1. Authentication & Authorization
- **Custom backend** (`users/backends.py`): Supports email, username, or handle authentication
- **Password validation**: Includes complexity, similarity, and common password checks
- **User permissions**: Enforced at view and model level

### 2. File Upload Validation
Located in `attachments/validators.py`:
- **Extension validation**: Only allows specific file types
- **MIME type validation**: Verifies actual file type matches extension
- **File size limits**: Different limits per file type
  - Images: 25 MB
  - Videos: 500 MB
  - Audio: 100 MB
  - Documents: 50 MB

Supported file types:
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`
- Videos: `.mp4`, `.webm`, `.avi`, `.mov`, `.mkv`
- Audio: `.mp3`, `.wav`, `.m4a`, `.ogg`
- Documents: `.pdf`, `.doc`, `.docx`, `.txt`, `.xlsx`, `.xls`

### 3. CORS & CSRF Protection
- CORS configured with allowed origins (see `settings.py`)
- CSRF protection enabled by default
- WebSocket connections require authentication

### 4. Rate Limiting
Configured in `settings.py`:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

Adjust via `DEFAULT_THROTTLE_RATES` in settings.

### 5. Database Security
- Parameterized queries (Django ORM)
- Connection pooling with `psycopg2`
- Indexed fields for query optimization

### 6. Logging & Monitoring
Comprehensive logging configured in `settings.py`:
- Debug logs go to console
- Error logs stored in `logs/django.log`
- Rotating log handler (10 MB max per file, 10 backups)

Monitor for:
- Authentication failures
- File upload violations
- Database errors
- Security warnings

### 7. API Throttling
Rate limiting prevents:
- Brute force attacks
- DoS attempts
- Spam

Current rates in `settings.py`:
- Adjust `DEFAULT_THROTTLE_RATES` as needed
- Can be overridden per viewset

## Production Deployment

### Docker Deployment
Using provided `docker-compose.yml`:

```bash
# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### SSL/TLS Configuration
1. Use a reverse proxy (Nginx, HAProxy)
2. Enable SSL certificates (Let's Encrypt recommended)
3. Set these in production `.env`:
   ```
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   ```

### Database Backups
```bash
# PostgreSQL backup
pg_dump -U postgres retronetwork > backup.sql

# Restore from backup
psql -U postgres retronetwork < backup.sql
```

### Redis Setup
For production messaging reliability:
1. Install Redis server
2. Configure persistence (RDB or AOF)
3. Set password authentication
4. Monitor memory usage

```bash
# Docker Redis
docker run -d -p 6379:6379 redis:7-alpine
```

## Security Checklist

### Before Deployment
- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure Redis server
- [ ] Set all SSL/TLS settings to `True`
- [ ] Configure email backend for password resets
- [ ] Review and adjust rate limits
- [ ] Set up log monitoring
- [ ] Configure static/media file serving
- [ ] Run `python manage.py check --deploy`

### Regular Maintenance
- [ ] Monitor logs for errors/attacks
- [ ] Update dependencies regularly
- [ ] Rotate database backups
- [ ] Check disk space for logs and media
- [ ] Review and update ALLOWED_HOSTS if needed
- [ ] Monitor Redis memory usage
- [ ] Review rate limit effectiveness

## Vulnerability Mitigation

### SQL Injection
✅ Protected by Django ORM parameterized queries

### XSS (Cross-Site Scripting)
✅ Django template auto-escaping
✅ CSRF token validation

### CSRF (Cross-Site Request Forgery)
✅ Django CSRF middleware
✅ CSRF token in forms

### File Upload Attacks
✅ Extension + MIME type validation
✅ File size limits
✅ Stored in `/media` directory outside web root (with Nginx)
✅ Served with appropriate headers

### Brute Force Attacks
✅ Rate limiting on API
✅ Django security middleware
✅ Account lockout possible (can be added)

### DDoS Attacks
✅ Rate limiting
✅ CDN recommended for static files
✅ Load balancer for scaling

### Session Hijacking
✅ Secure cookies configured
✅ HTTPS enforced in production
✅ Session timeout possible (can be configured)

## Additional Recommendations

1. **Two-Factor Authentication (2FA)**: Consider adding `django-otp` package
2. **API Documentation**: Secure with API key authentication
3. **User Audit Logs**: Track user actions for security review
4. **Content Filtering**: Add profanity/spam filters
5. **Rate Limiting**: Monitor and adjust thresholds based on usage
6. **Security Headers**: Review and add additional headers as needed
7. **Dependency Updates**: Use tools like Snyk or Dependabot

## Support & Reporting
For security issues, please report responsibly to the maintainers.
