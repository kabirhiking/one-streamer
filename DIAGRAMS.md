# System Diagrams

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    React Frontend                        │  │
│  │                    (Port 3000)                           │  │
│  │                                                          │  │
│  │  • Video Player (Video.js)                              │  │
│  │  • Upload Interface                                      │  │
│  │  • User Dashboard                                        │  │
│  │  • Analytics View                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REVERSE PROXY LAYER                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      Nginx                               │  │
│  │                    (Port 8080)                           │  │
│  │                                                          │  │
│  │  • Reverse Proxy                                         │  │
│  │  • HLS Streaming                                         │  │
│  │  • Load Balancing                                        │  │
│  │  • Rate Limiting                                         │  │
│  └──────┬─────────────────────────┬─────────────────────────┘  │
└─────────┼─────────────────────────┼─────────────────────────────┘
          │                         │
          │                         │
          ▼                         ▼
┌──────────────────────┐   ┌──────────────────────┐
│   APPLICATION LAYER  │   │   APPLICATION LAYER  │
│                      │   │                      │
│  ┌────────────────┐ │   │  ┌────────────────┐ │
│  │     Django     │ │   │  │    FastAPI     │ │
│  │   (Port 8000)  │ │   │  │  (Port 8001)   │ │
│  │                │ │   │  │                │ │
│  │ • Auth         │ │   │  │ • Video API    │ │
│  │ • Users        │ │   │  │ • Upload       │ │
│  │ • Admin        │ │   │  │ • Streaming    │ │
│  └────────┬───────┘ │   │  └────────┬───────┘ │
└───────────┼─────────┘   └───────────┼─────────┘
            │                         │
            │                         │
            └────────┬────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL                            │  │
│  │                    (Port 5432)                           │  │
│  │                                                          │  │
│  │  Tables:                                                 │  │
│  │  • users            • videos                            │  │
│  │  • subscriptions    • video_files                       │  │
│  │  • comments         • likes                             │  │
│  │  • watch_history    • video_analytics                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                           │
│                                                                 │
│  ┌──────────────────┐          ┌──────────────────────────┐    │
│  │      Redis       │◄─────────│   Celery Workers         │    │
│  │   (Port 6379)    │          │                          │    │
│  │                  │          │  • Video Encoding        │    │
│  │  • Task Queue    │          │  • FFmpeg Processing     │    │
│  │  • Results       │          │  • HLS Conversion        │    │
│  │  • Cache         │          │  • Thumbnail Gen         │    │
│  └──────────────────┘          └──────────┬───────────────┘    │
└───────────────────────────────────────────┼───────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      MinIO                               │  │
│  │              (Port 9000, Console 9001)                   │  │
│  │                                                          │  │
│  │  Buckets:                                                │  │
│  │  • videos/                                               │  │
│  │    ├── {video_id}/                                       │  │
│  │    │   ├── master.m3u8                                   │  │
│  │    │   ├── 360p/                                         │  │
│  │    │   ├── 480p/                                         │  │
│  │    │   ├── 720p/                                         │  │
│  │    │   └── 1080p/                                        │  │
│  │  • thumbnails/                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Video Upload Flow

```
┌────────┐
│  User  │
└───┬────┘
    │ 1. Select video file
    ▼
┌────────────┐
│   React    │
│  Frontend  │
└─────┬──────┘
      │ 2. POST /api/upload/ (FormData with file)
      ▼
┌────────────┐
│  FastAPI   │
│   Upload   │
└─────┬──────┘
      │ 3. Save to temp storage
      │ 4. Create video record in DB
      ▼
┌────────────┐
│ PostgreSQL │
└─────┬──────┘
      │ 5. Queue Celery task
      ▼
┌────────────┐
│   Redis    │
│Task Queue  │
└─────┬──────┘
      │ 6. Worker picks up task
      ▼
┌────────────────────────────────────────┐
│          Celery Worker                 │
│                                        │
│  7. Read video file                    │
│  8. Get video info (duration, etc)     │
│  9. Encode to 360p → Upload to MinIO   │
│ 10. Encode to 480p → Upload to MinIO   │
│ 11. Encode to 720p → Upload to MinIO   │
│ 12. Encode to 1080p → Upload to MinIO  │
│ 13. Create master playlist              │
│ 14. Generate thumbnail                  │
│ 15. Upload all to MinIO                │
│ 16. Update DB status to 'ready'        │
└──────────┬─────────────────────────────┘
           │
           ▼
      ┌─────────┐
      │  MinIO  │
      │ Storage │
      └─────────┘
```

## Video Streaming Flow

```
┌────────┐
│  User  │
└───┬────┘
    │ 1. Click video
    ▼
┌────────────┐
│   React    │
└─────┬──────┘
      │ 2. GET /api/videos/{id}
      │ 3. GET /api/stream/token/{id}
      ▼
┌────────────┐
│  FastAPI   │
└─────┬──────┘
      │ 4. Return video metadata
      │ 5. Generate streaming token
      │ 6. Return HLS URL with token
      ▼
┌────────────┐
│   React    │
│  Video.js  │
└─────┬──────┘
      │ 7. Request master.m3u8
      ▼
┌────────────┐
│   Nginx    │
└─────┬──────┘
      │ 8. Proxy to MinIO
      ▼
┌────────────┐
│   MinIO    │
└─────┬──────┘
      │ 9. Return master playlist
      ▼
┌────────────┐
│  Video.js  │
└─────┬──────┘
      │ 10. Choose quality (e.g., 720p)
      │ 11. Request 720p/playlist.m3u8
      ▼
┌────────────┐
│   Nginx    │ → MinIO
└─────┬──────┘
      │ 12. Return quality playlist
      ▼
┌────────────┐
│  Video.js  │
└─────┬──────┘
      │ 13. Request segments (segment_000.ts, etc)
      │ 14. Download and play segments
      ▼
┌────────────┐
│   Nginx    │ → MinIO → Video segments
└────────────┘
      │
      │ 15. Stream plays smoothly!
      ▼
┌────────────┐
│   User     │
│  Watching  │
└────────────┘
```

## Authentication Flow

```
┌────────┐
│  User  │
└───┬────┘
    │ 1. Enter email & password
    ▼
┌────────────┐
│   React    │
└─────┬──────┘
      │ 2. POST /api/auth/login/
      ▼
┌────────────┐
│   Django   │
└─────┬──────┘
      │ 3. Validate credentials
      │ 4. Generate JWT tokens
      ▼
┌────────────┐
│  Response  │
│  {         │
│    access  │
│    refresh │
│  }         │
└─────┬──────┘
      │ 5. Store in localStorage
      ▼
┌────────────┐
│   React    │
│   State    │
└─────┬──────┘
      │ 6. Include in API requests
      │    Authorization: Bearer {token}
      ▼
┌────────────┐
│  FastAPI/  │
│   Django   │
└─────┬──────┘
      │ 7. Validate JWT
      │ 8. Extract user_id
      │ 9. Process request
      ▼
┌────────────┐
│  Response  │
└────────────┘
```

## Database Schema Relationships

```
┌──────────────┐
│    users     │
├──────────────┤
│ id (PK)      │
│ email        │
│ password     │
│ is_creator   │
└──────┬───────┘
       │
       │ created by
       ▼
┌──────────────┐        ┌──────────────┐
│    videos    │───────▶│ video_files  │
├──────────────┤  has   ├──────────────┤
│ id (PK)      │        │ id (PK)      │
│ creator_id   │        │ video_id(FK) │
│ title        │        │ quality      │
│ status       │        │ playlist_url │
└──────┬───────┘        └──────────────┘
       │
       │ has
       ▼
┌──────────────┐
│   comments   │
├──────────────┤
│ id (PK)      │
│ video_id(FK) │
│ user_id (FK) │
│ parent_id    │
└──────┬───────┘
       │
       │ can have
       ▼
┌──────────────┐
│    likes     │
├──────────────┤
│ id (PK)      │
│ user_id (FK) │
│ video_id(FK) │
│ comment_id   │
│ like_type    │
└──────────────┘

┌──────────────┐        ┌──────────────┐
│    users     │◀──────│subscriptions │
├──────────────┤        ├──────────────┤
│ id (PK)      │        │ id (PK)      │
│              │        │subscriber_id │
│              │        │ creator_id   │
└──────────────┘        └──────────────┘
       │
       │ tracks
       ▼
┌──────────────┐
│watch_history │
├──────────────┤
│ id (PK)      │
│ user_id (FK) │
│ video_id(FK) │
│ watch_time   │
│ completed    │
└──────────────┘
```

## Service Dependencies

```
                  ┌──────────────┐
                  │  PostgreSQL  │
                  └───────┬──────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
  ┌──────────┐      ┌──────────┐     ┌──────────┐
  │  Django  │      │ FastAPI  │     │  Celery  │
  └────┬─────┘      └────┬─────┘     └────┬─────┘
       │                 │                 │
       │                 │                 │
       └────────┬────────┴────────┬────────┘
                │                 │
                ▼                 ▼
          ┌──────────┐      ┌──────────┐
          │  Nginx   │      │  MinIO   │
          └──────────┘      └──────────┘
                                  ▲
                                  │
                            ┌─────┴─────┐
                            │  Celery   │
                            │  Workers  │
                            └───────────┘

         ┌──────────┐
         │  Redis   │◀───── All services use for caching
         └──────────┘
```

## Deployment Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Environment                  │
│                                                             │
│  ┌─────────────┐                                           │
│  │   CDN       │ ← Static files & HLS segments             │
│  └──────┬──────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────┐                                           │
│  │ Load        │                                            │
│  │ Balancer    │                                            │
│  └──────┬──────┘                                           │
│         │                                                   │
│    ┌────┴────┐                                             │
│    │         │                                              │
│    ▼         ▼                                              │
│  ┌────┐   ┌────┐   ┌────┐                                 │
│  │App1│   │App2│   │App3│  ← Horizontal scaling           │
│  └─┬──┘   └─┬──┘   └─┬──┘                                 │
│    │        │        │                                      │
│    └────────┼────────┘                                     │
│             │                                               │
│             ▼                                               │
│    ┌────────────────┐                                      │
│    │   Database     │                                       │
│    │   Cluster      │ ← Master + Replicas                  │
│    └────────────────┘                                      │
│                                                             │
│    ┌────────────────┐                                      │
│    │   Redis        │                                       │
│    │   Cluster      │ ← HA setup                           │
│    └────────────────┘                                      │
│                                                             │
│    ┌────────────────┐                                      │
│    │   MinIO        │                                       │
│    │   Distributed  │ ← Multi-node                         │
│    └────────────────┘                                      │
│                                                             │
│  ┌──────────────────────────────────┐                     │
│  │    Celery Worker Pool            │                      │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐   │                     │
│  │  │ W1 │ │ W2 │ │ W3 │ │ W4 │   │ ← Auto-scaling      │
│  │  └────┘ └────┘ └────┘ └────┘   │                     │
│  └──────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

These diagrams provide a visual understanding of the system architecture and workflows!
