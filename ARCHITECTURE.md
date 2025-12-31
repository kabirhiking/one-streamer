# Video Streaming Platform - Architecture Documentation

## System Overview

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  React Frontend │ (Port 3000)
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │  Nginx │ (Port 8080)
    └────┬───┘
         │
    ┌────┴──────────────────────┐
    ▼                           ▼
┌──────────┐            ┌──────────────┐
│  Django  │            │   FastAPI    │
│ (Auth)   │            │  (Videos)    │
│  :8000   │            │    :8001     │
└────┬─────┘            └──────┬───────┘
     │                         │
     └──────────┬──────────────┘
                ▼
         ┌─────────────┐
         │ PostgreSQL  │
         │   :5432     │
         └─────────────┘

┌──────────────┐       ┌─────────────┐
│    Redis     │◄──────│   Celery    │
│    :6379     │       │   Workers   │
└──────────────┘       └──────┬──────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   MinIO     │
                       │ (Storage)   │
                       │  :9000      │
                       └─────────────┘
```

## Component Responsibilities

### Frontend (React)
- User interface
- Video playback (HLS)
- Authentication state management
- API communication

### Nginx
- Reverse proxy
- Static file serving
- HLS video delivery
- Load balancing
- SSL termination

### Django
- User authentication (JWT)
- User management
- Subscription management
- Admin panel
- Database models (Users, Subscriptions)

### FastAPI
- Video metadata API
- Upload handling
- Streaming token generation
- Analytics endpoints
- Database queries (Videos, Comments, Likes)

### Celery Workers
- Video encoding (FFmpeg)
- HLS conversion
- Thumbnail generation
- MinIO upload
- Background tasks

### PostgreSQL
- Relational data storage
- User accounts
- Video metadata
- Comments, likes, subscriptions
- Analytics data

### Redis
- Celery message broker
- Task result backend
- Caching layer
- Session storage

### MinIO
- Object storage (S3-compatible)
- Video files (HLS segments)
- Thumbnails
- Original uploads

## Data Flow

### Video Upload Flow

1. User uploads video via React frontend
2. FastAPI receives file and creates database record
3. File saved to temporary storage
4. Celery task queued for processing
5. Worker downloads file, encodes to HLS
6. Multiple quality levels generated (360p, 480p, 720p, 1080p)
7. HLS playlists and segments created
8. Files uploaded to MinIO
9. Database updated with URLs and status
10. Temporary files cleaned up

### Video Playback Flow

1. User requests video page
2. React fetches video metadata from FastAPI
3. FastAPI returns video info and generates streaming token
4. React initializes Video.js player with HLS URL
5. Player requests master playlist from Nginx
6. Nginx proxies request to MinIO
7. Player selects quality and requests segments
8. Video streams with adaptive bitrate

### Authentication Flow

1. User logs in via React
2. Request sent to Django /api/auth/login/
3. Django validates credentials
4. JWT tokens generated (access + refresh)
5. Tokens stored in localStorage
6. Access token sent with subsequent requests
7. Token validated by middleware
8. Refresh token used when access expires

## Database Schema

### Users Table
```sql
users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(254) UNIQUE NOT NULL,
  password VARCHAR(128) NOT NULL,
  display_name VARCHAR(100),
  bio TEXT,
  avatar VARCHAR(200),
  is_creator BOOLEAN DEFAULT FALSE,
  channel_name VARCHAR(100),
  channel_description TEXT,
  subscribers_count INTEGER DEFAULT 0,
  total_views BIGINT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Videos Table
```sql
videos (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  creator_id INTEGER REFERENCES users(id),
  thumbnail VARCHAR(200),
  duration INTEGER DEFAULT 0,
  file_size BIGINT DEFAULT 0,
  status VARCHAR(20) DEFAULT 'processing',
  visibility VARCHAR(20) DEFAULT 'public',
  views_count BIGINT DEFAULT 0,
  likes_count INTEGER DEFAULT 0,
  dislikes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  hls_master_url VARCHAR(200),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  published_at TIMESTAMP
)
```

### VideoFiles Table
```sql
video_files (
  id SERIAL PRIMARY KEY,
  video_id INTEGER REFERENCES videos(id),
  quality VARCHAR(10),
  playlist_url VARCHAR(200),
  file_size BIGINT DEFAULT 0,
  bitrate INTEGER DEFAULT 0,
  created_at TIMESTAMP,
  UNIQUE(video_id, quality)
)
```

### Comments Table
```sql
comments (
  id SERIAL PRIMARY KEY,
  video_id INTEGER REFERENCES videos(id),
  user_id INTEGER REFERENCES users(id),
  parent_id INTEGER REFERENCES comments(id),
  content TEXT NOT NULL,
  likes_count INTEGER DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Likes Table
```sql
likes (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  video_id INTEGER REFERENCES videos(id),
  comment_id INTEGER REFERENCES comments(id),
  like_type VARCHAR(10) NOT NULL,
  created_at TIMESTAMP,
  UNIQUE(user_id, video_id),
  UNIQUE(user_id, comment_id)
)
```

### Subscriptions Table
```sql
subscriptions (
  id SERIAL PRIMARY KEY,
  subscriber_id INTEGER REFERENCES users(id),
  creator_id INTEGER REFERENCES users(id),
  created_at TIMESTAMP,
  UNIQUE(subscriber_id, creator_id)
)
```

## Security Implementation

### Authentication
- JWT tokens with RS256 algorithm
- Access token: 30 minutes expiry
- Refresh token: 7 days expiry
- Token rotation on refresh
- Blacklist for revoked tokens

### Authorization
- Role-based access control
- Creator-only endpoints
- Video visibility controls
- Private video access checks

### Video Streaming
- Signed URLs with expiration
- Token-based HLS access
- Hotlink protection
- Rate limiting

### API Security
- CORS configuration
- CSRF protection
- SQL injection prevention (ORM)
- XSS protection
- Input validation
- File upload restrictions

## Performance Optimizations

### Database
- Indexed frequently queried fields
- Connection pooling
- Query optimization
- Denormalized counters

### Caching
- Redis for session data
- API response caching
- Video metadata caching
- Static file caching

### Video Delivery
- HLS adaptive streaming
- CDN integration ready
- Segment caching
- Parallel downloads

### Scalability
- Horizontal service scaling
- Background task processing
- Asynchronous operations
- Load balancing ready

## Monitoring and Logging

### Health Checks
- `/health` endpoints on all services
- Database connectivity checks
- Storage availability checks

### Logging
- Structured JSON logs
- Error tracking
- Access logs
- Performance metrics

### Metrics
- Video upload success rate
- Encoding completion time
- API response times
- Storage usage
- Active users
- Video views

## Deployment Strategy

### Development
- Docker Compose for local development
- Hot reload enabled
- Debug mode active
- Sample data included

### Production
- Container orchestration (Kubernetes/ECS)
- Environment-based configuration
- Secrets management
- SSL/TLS enabled
- CDN integration
- Database backups
- Monitoring dashboards
- Auto-scaling policies

## Technology Decisions

### Why Django + FastAPI?
- Django: Mature auth system, admin panel
- FastAPI: High performance for video APIs, async support
- Separation of concerns
- Best tool for each job

### Why PostgreSQL?
- ACID compliance
- Complex queries support
- Mature ecosystem
- Great performance

### Why MinIO?
- S3-compatible API
- Self-hosted option
- Easy migration to AWS S3
- Cost-effective

### Why HLS?
- Universal browser support
- Adaptive bitrate streaming
- Industry standard
- DRM support available

### Why Celery?
- Reliable task queue
- Python ecosystem
- Retry mechanisms
- Monitoring tools
