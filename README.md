# RetroNetwork

A classic social network application built with Django, Django REST Framework, and Django Channels for real-time messaging.

## Features

- 👥 **User Profiles**: Customizable profiles with status, bio, and avatars
- 📝 **Posts & Comments**: Create and interact with posts and comments
- ❤️ **Reactions**: Like posts and leave reactions on messages
- 💬 **Real-time Messaging**: WebSocket-based instant messaging with typing indicators
- 🔔 **Notifications**: Real-time notifications for interactions
- 🔒 **Privacy Controls**: Block users, manage followers, customize privacy settings
- 📎 **Media Handling**: Support for images, videos, and documents
- 🔍 **Search**: Search posts and users
- 🌓 **Dark Theme**: Built-in dark theme support

## Tech Stack

- **Backend**: Django 6.0.2
- **API**: Django REST Framework 3.16.1
- **Real-time**: Django Channels 4.3.2 with WebSockets
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Caching/Messaging**: Redis
- **Media Processing**: Pillow
- **ASGI Server**: Daphne

## Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RetroNetwork
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

   The application will be available at `http://localhost:8000`

### Docker Setup

```bash
docker-compose up -d
```

Access the application at `http://localhost:8000`

## Project Structure

```
RetroNetwork/
├── users/              # User authentication and profiles
├── posts/              # Posts and post management
├── comments/           # Comments on posts
├── reactions/          # Likes and reactions
├── messaging/          # Real-time messaging
├── notifications/      # Notification system
├── user_settings/      # User settings and privacy
├── attachments/        # File upload handling
├── social_core/        # Project configuration
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, images
└── media/              # User uploaded files
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `SECRET_KEY`: Django secret key (generate new one for production)
- `DEBUG`: Debug mode (False for production)
- `ALLOWED_HOSTS`: Allowed host domains
- `DATABASE_URL`: Database connection string
- `REDIS_HOST`: Redis server host

### Security

**IMPORTANT**: See [SECURITY.md](SECURITY.md) for production deployment security guidelines.

## API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `POST /accounts/register/` - User registration

### Users
- `GET /accounts/<handle>/` - View user profile
- `GET /accounts/search/` - Search users
- `POST /accounts/<handle>/follow/` - Follow user

### Posts
- `GET /` - List posts
- `POST /` - Create post
- `GET /<id>/` - View post detail
- `PUT /<id>/` - Update post
- `DELETE /<id>/` - Delete post

### Messaging
- `GET /api/messages/` - List conversations
- `POST /api/messages/` - Create conversation
- `GET /api/messages/<id>/` - Get messages in conversation

### WebSocket
- `ws://localhost:8000/ws/chat/<conversation_id>/` - Real-time messaging

## File Upload Validation

Files are validated by:
1. Extension checking
2. MIME type verification
3. File size limits

Supported formats:
- **Images**: JPG, PNG, GIF, WebP, SVG (max 25MB)
- **Videos**: MP4, WebM, AVI, MOV, MKV (max 500MB)
- **Audio**: MP3, WAV, M4A, OGG (max 100MB)
- **Documents**: PDF, DOC, DOCX, TXT, XLS, XLSX (max 50MB)

## Rate Limiting

API rate limits:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour

## Database Models

### User
- Profile information (handle, display name, bio)
- Avatar and status
- Privacy settings

### Post
- Content and media
- View count
- Timestamps

### Comment
- Author and content
- Associated post
- Timestamps

### Message
- Real-time messaging
- Multiple file types
- Read receipts

### Conversation
- Group or direct messaging
- Participant management
- Message history

## Testing

Run tests:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test users
```

## Populating Test Data

Generate test data to quickly populate your database for development and testing:

### Create Test Posts
```bash
python manage.py create_test_posts
```
Creates sample posts with various content and media types for all users in the system.

### Create Test Messages
```bash
python manage.py create_test_messages
```
Creates sample conversations and messages between users for testing the messaging system.

## Logging

Logs are configured in `settings.py`:
- **Console output**: INFO level
- **File logs**: `logs/django.log` (ERROR level)
- **Rotating handler**: 10MB max file size, 10 backups

## Performance Optimization

- Database query optimization with `select_related()` and `prefetch_related()`
- Indexed database fields
- Redis caching for WebSockets
- Media file size limits and validation
- Pagination for list views

## Contributing

1. Create a feature branch
2. Make your changes
3. Ensure tests pass
4. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Support

For issues and questions, please open an issue on the repository.

## Roadmap

- [ ] Two-factor authentication
- [ ] User blocking improvements
- [ ] Message encryption
- [ ] Video call support
- [ ] Group chat features
- [ ] User analytics dashboard
- [ ] Content moderation tools
