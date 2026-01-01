# API Documentation

## Authentication Endpoints

### Register User

**POST** `/api/auth/register/`

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "password_confirm": "SecurePassword123",
  "display_name": "John Doe",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "is_creator": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Login

**POST** `/api/auth/login/`

```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

### Get Profile

**GET** `/api/auth/profile/`

Headers: `Authorization: Bearer <access_token>`

### Become Creator

**POST** `/api/auth/become-creator/`

```json
{
  "channel_name": "My Channel"
}
```

## Video Endpoints

### List Videos

**GET** `/api/videos/?page=1&page_size=20`

### Get Video

**GET** `/api/videos/{video_id}`

### Update Video

**PUT** `/api/videos/{video_id}`

```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "visibility": "public"
}
```

### Delete Video

**DELETE** `/api/videos/{video_id}`

## Upload Endpoints

### Upload Video

**POST** `/api/upload/`

Form Data:
- `file`: Video file
- `title`: Video title
- `description`: Video description
- `visibility`: public|unlisted|private

### Check Upload Status

**GET** `/api/upload/status/{video_id}`

## Streaming Endpoints

### Get Streaming Token

**GET** `/api/stream/token/{video_id}`

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_at": "2024-01-01T00:00:00Z",
  "hls_url": "http://localhost:8080/videos/1/master.m3u8?token=..."
}
```

### Update Watch Progress

**POST** `/api/stream/progress`

```json
{
  "video_id": 1,
  "watch_time": 120,
  "completed": false
}
```

## Analytics Endpoints

### Get Video Analytics

**GET** `/api/analytics/video/{video_id}`

### Get Creator Analytics

**GET** `/api/analytics/creator`

### Get Trending Videos

**GET** `/api/analytics/trending?days=7`

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message"
}
```

HTTP Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
