# Video Streaming Platform

A full-featured video streaming platform with adaptive streaming, social features, and analytics.

## 🎯 Features

- **Video Upload & Processing**: Upload videos with automatic transcoding to HLS format
- **Adaptive Streaming**: HLS-based streaming with multiple quality levels
- **Authentication**: JWT-based user authentication and authorization
- **Social Features**: Comments, likes/dislikes, subscriptions
- **Creator Dashboard**: Analytics for video performance
- **Security**: Token-based video access, rate limiting, hotlink protection

## 🏗️ Architecture

- **Backend**: Django (Auth) + FastAPI (Video Services)
- **Frontend**: React
- **Database**: PostgreSQL
- **Storage**: MinIO (S3-compatible)
- **Streaming**: HLS via Nginx
- **Encoding**: FFmpeg with Celery workers
- **Cache**: Redis
- **Deployment**: Docker & Docker Compose

## 📁 Project Structure

```
video-streaming-platform/
├── backend/
│   ├── django_auth/          # Django authentication service
│   ├── fastapi_video/        # FastAPI video service
│   └── common/               # Shared utilities
├── frontend/
│   └── react-app/            # React frontend
├── workers/
│   └── celery_workers/       # Video encoding workers
├── nginx/
│   └── config/               # Nginx configuration
├── docker/                   # Docker configurations
└── docker-compose.yml        # Orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd video-streaming-platform
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

5. Access the application:
- Frontend: http://localhost:3000
- Django Admin: http://localhost:8000/admin
- FastAPI Docs: http://localhost:8001/docs
- MinIO Console: http://localhost:9001

## 🔧 Development

### Backend Development

```bash
# Django
cd backend/django_auth
python manage.py runserver

# FastAPI
cd backend/fastapi_video
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend/react-app
npm install
npm start
```

### Running Tests

```bash
# Django tests
docker-compose exec django python manage.py test

# FastAPI tests
docker-compose exec fastapi pytest
```

## 📊 Database Schema

### Core Tables
- **Users**: User accounts and profiles
- **Videos**: Video metadata
- **VideoFiles**: HLS segments and quality variants
- **Comments**: User comments
- **Likes**: Video likes/dislikes
- **Subscriptions**: Channel subscriptions
- **Analytics**: Video performance metrics

## 🔐 Security Features

- JWT token authentication
- Signed video URLs with expiration
- Rate limiting on API endpoints
- CORS configuration
- Hotlink protection
- Password hashing with bcrypt

## 📈 Scaling Strategy

- Horizontal scaling for all services
- Background task processing with Celery
- Redis caching for frequently accessed data
- CDN-compatible HLS delivery
- Database connection pooling

## 🌐 API Documentation

- Django API: http://localhost:8000/api/docs
- FastAPI: http://localhost:8001/docs

## 📝 License

MIT License

## 👨‍💻 Author

Portfolio Project - Showcasing full-stack development skills with modern technologies
