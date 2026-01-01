# Development Setup Guide

## Prerequisites

- Docker Desktop installed
- Git
- 8GB RAM minimum
- 20GB free disk space

## Quick Start

### 1. Clone and Setup

```powershell
cd "c:\Users\Pc\Desktop\AI writer"
```

### 2. Create Environment File

```powershell
Copy-Item .env.example .env
```

Edit `.env` file if needed (defaults work for development).

### 3. Start Services

```powershell
docker-compose up -d
```

This will start all services:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (ports 9000, 9001)
- Django (port 8000)
- FastAPI (port 8001)
- Nginx (port 8080)
- React Frontend (port 3000)
- Celery Workers

### 4. Run Database Migrations

```powershell
docker-compose exec django python manage.py migrate
```

### 5. Create Superuser

```powershell
docker-compose exec django python manage.py createsuperuser
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Django Admin**: http://localhost:8000/admin
- **FastAPI Docs**: http://localhost:8001/docs
- **MinIO Console**: http://localhost:9001
  - Username: minioadmin
  - Password: minioadmin123

## Development Workflow

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f django
docker-compose logs -f fastapi
docker-compose logs -f celery_worker
```

### Restart Services

```powershell
# Restart specific service
docker-compose restart django

# Restart all
docker-compose restart
```

### Stop Services

```powershell
docker-compose down
```

### Stop and Remove Data

```powershell
docker-compose down -v
```

## Database Management

### Access PostgreSQL

```powershell
docker-compose exec postgres psql -U postgres -d video_streaming_db
```

### Create Migrations

```powershell
docker-compose exec django python manage.py makemigrations
docker-compose exec django python manage.py migrate
```

### Django Shell

```powershell
docker-compose exec django python manage.py shell
```

## Testing Video Upload

1. Register a new account at http://localhost:3000/register
2. Login with your credentials
3. Go to Upload page
4. Select a video file (MP4, AVI, MOV, or MKV)
5. Fill in title and description
6. Click Upload
7. Wait for processing (check Celery worker logs)
8. Video will be available for streaming when status is "ready"

## Troubleshooting

### Services Won't Start

```powershell
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs django
```

### Database Connection Error

```powershell
# Ensure PostgreSQL is healthy
docker-compose ps postgres

# Restart database
docker-compose restart postgres
```

### MinIO Connection Error

```powershell
# Restart MinIO and client
docker-compose restart minio minio_client
```

### Video Processing Fails

```powershell
# Check Celery worker logs
docker-compose logs celery_worker

# Ensure FFmpeg is available
docker-compose exec celery_worker ffmpeg -version
```

### Frontend Can't Connect to Backend

- Verify Django is running: http://localhost:8000/api/health/
- Verify FastAPI is running: http://localhost:8001/health
- Check CORS settings in Django settings.py
- Clear browser cache

## Production Deployment

### Environment Variables

Update `.env` file with production values:

```env
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com
DJANGO_SECRET_KEY=generate-a-secure-key
JWT_SECRET_KEY=generate-a-secure-jwt-key
MINIO_ROOT_USER=change-this
MINIO_ROOT_PASSWORD=change-this
```

### SSL/TLS

Configure Nginx with SSL certificates:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    # ... rest of configuration
}
```

### Scaling

Scale Celery workers:

```powershell
docker-compose up -d --scale celery_worker=4
```

Scale FastAPI:

```powershell
docker-compose up -d --scale fastapi=3
```

## Performance Optimization

### Database

- Enable connection pooling
- Add database indices for frequently queried fields
- Use read replicas for analytics queries

### Video Storage

- Configure CDN for MinIO (CloudFront, CloudFlare)
- Enable MinIO lifecycle policies for old content
- Use object versioning

### Caching

- Implement Redis caching for API responses
- Cache video metadata
- Use browser caching for static assets

## Monitoring

### Service Health Checks

- Django: http://localhost:8000/api/health/
- FastAPI: http://localhost:8001/health
- Nginx: http://localhost:8080/health

### Resource Usage

```powershell
docker stats
```

## Backup and Recovery

### Database Backup

```powershell
docker-compose exec postgres pg_dump -U postgres video_streaming_db > backup.sql
```

### Database Restore

```powershell
cat backup.sql | docker-compose exec -T postgres psql -U postgres video_streaming_db
```

### MinIO Backup

Use MinIO client to sync buckets or configure bucket replication.
