# Testing Guide

## Testing the Video Streaming Platform

### Prerequisites

Ensure all services are running:
```powershell
docker-compose ps
```

All services should show "Up" status.

## 1. Authentication Testing

### Register a New User

1. Navigate to http://localhost:3000/register
2. Fill in the registration form:
   - Email: test@example.com
   - Display Name: Test User
   - Password: TestPassword123
   - Confirm Password: TestPassword123
3. Click "Sign Up"
4. You should be redirected to the home page

### Login

1. Navigate to http://localhost:3000/login
2. Enter credentials:
   - Email: test@example.com
   - Password: TestPassword123
3. Click "Login"
4. You should see the upload and profile options in the header

### API Testing (Postman/cURL)

**Register:**
```powershell
curl -X POST http://localhost:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d '{
    "email": "api@example.com",
    "password": "ApiTest123",
    "password_confirm": "ApiTest123",
    "display_name": "API User"
  }'
```

**Login:**
```powershell
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{
    "email": "api@example.com",
    "password": "ApiTest123"
  }'
```

Save the `access` token from the response.

## 2. Video Upload Testing

### Via Web Interface

1. Login to http://localhost:3000
2. Click "Upload" in the navigation
3. Select a video file (test with a short MP4 file)
4. Fill in:
   - Title: "Test Video"
   - Description: "This is a test video"
   - Visibility: Public
5. Click "Upload Video"
6. Monitor the upload progress
7. Check Celery worker logs for processing:
   ```powershell
   docker-compose logs -f celery_worker
   ```

### Via API

```powershell
$token = "your-access-token"

curl -X POST http://localhost:8001/api/upload/ `
  -H "Authorization: Bearer $token" `
  -F "file=@C:\path\to\video.mp4" `
  -F "title=API Test Video" `
  -F "description=Uploaded via API" `
  -F "visibility=public"
```

### Check Upload Status

```powershell
curl -X GET http://localhost:8001/api/upload/status/1 `
  -H "Authorization: Bearer $token"
```

## 3. Video Processing Testing

### Monitor Processing

Watch Celery worker logs:
```powershell
docker-compose logs -f celery_worker
```

You should see:
1. "Processing video X: Title"
2. "Encoding 360p..."
3. "Encoding 480p..."
4. "Encoding 720p..."
5. "Encoding 1080p..."
6. "Creating master playlist..."
7. "Generating thumbnail..."
8. "Uploading to storage..."
9. "Video X processed successfully"

### Verify MinIO Upload

1. Navigate to http://localhost:9001
2. Login with:
   - Username: minioadmin
   - Password: minioadmin123
3. Browse to the "videos" bucket
4. You should see:
   - `videos/1/master.m3u8`
   - `videos/1/360p/playlist.m3u8`
   - `videos/1/360p/segment_*.ts`
   - Similar folders for other qualities
   - `thumbnails/1.jpg`

## 4. Video Playback Testing

### Web Player

1. Navigate to http://localhost:3000
2. Click on a video card
3. Video should start playing automatically
4. Test quality switching (if your player supports it)
5. Test pause/play controls
6. Test seeking (dragging the progress bar)
7. Test volume control

### Direct HLS Access

Get streaming token:
```powershell
curl -X GET http://localhost:8001/api/stream/token/1 `
  -H "Authorization: Bearer $token"
```

Use the `hls_url` from response in a video player (VLC, etc.)

### Test Different Qualities

Access specific quality playlists:
- http://localhost:8080/videos/1/360p/playlist.m3u8
- http://localhost:8080/videos/1/480p/playlist.m3u8
- http://localhost:8080/videos/1/720p/playlist.m3u8
- http://localhost:8080/videos/1/1080p/playlist.m3u8

## 5. Social Features Testing

### Comments (Future Implementation)

Test comment creation, replies, and likes.

### Likes/Dislikes (Future Implementation)

Test video likes and dislikes.

### Subscriptions

**Subscribe to Creator via API:**
```powershell
curl -X POST http://localhost:8000/api/auth/subscriptions/ `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"creator_id": 1}'
```

**List Subscriptions:**
```powershell
curl -X GET http://localhost:8000/api/auth/subscriptions/ `
  -H "Authorization: Bearer $token"
```

## 6. Analytics Testing

### Video Analytics

```powershell
curl -X GET http://localhost:8001/api/analytics/video/1 `
  -H "Authorization: Bearer $token"
```

Should return:
- Total views
- Total watch time
- Average watch duration
- Completion rate
- Likes/dislikes
- Comments count

### Creator Analytics

```powershell
curl -X GET http://localhost:8001/api/analytics/creator `
  -H "Authorization: Bearer $token"
```

Should return:
- Total videos
- Total views
- Total likes
- Total comments
- List of videos with stats

### Via Dashboard

1. Login as a creator
2. Navigate to http://localhost:3000/dashboard
3. View analytics cards
4. Check video list with stats

## 7. Performance Testing

### Load Test Video Upload

Use Apache Bench or similar tool:
```powershell
# Not recommended with large video files
# Test with small files only
```

### Concurrent Video Playback

Open multiple browser tabs playing different videos.

### Check Resource Usage

```powershell
docker stats
```

Monitor CPU, memory, and network usage.

## 8. Error Handling Testing

### Invalid Login

Try logging in with wrong credentials:
```powershell
curl -X POST http://localhost:8000/api/auth/login/ `
  -H "Content-Type: application/json" `
  -d '{
    "email": "wrong@example.com",
    "password": "wrongpassword"
  }'
```

Should return 401 Unauthorized.

### Upload Without Authentication

Try uploading without token:
```powershell
curl -X POST http://localhost:8001/api/upload/ `
  -F "file=@video.mp4" `
  -F "title=Test"
```

Should return 401 Unauthorized.

### Access Private Video

Try accessing a private video as different user:
```powershell
curl -X GET http://localhost:8001/api/videos/1 `
  -H "Authorization: Bearer $different_user_token"
```

Should return 403 Forbidden if video is private.

### Upload Large File

Try uploading a file larger than 500MB (configured limit):
Should return 400 Bad Request with size limit error.

### Upload Invalid Format

Try uploading a non-video file:
Should return 400 Bad Request with format error.

## 9. Database Testing

### Check Data Integrity

Access PostgreSQL:
```powershell
docker-compose exec postgres psql -U postgres -d video_streaming_db
```

Run queries:
```sql
-- Count users
SELECT COUNT(*) FROM users;

-- Count videos
SELECT COUNT(*) FROM videos;

-- Check video status
SELECT id, title, status FROM videos;

-- Check video files
SELECT video_id, quality, playlist_url FROM video_files;

-- Check subscriptions
SELECT subscriber_id, creator_id FROM subscriptions;
```

### Check Watch History

```sql
SELECT user_id, video_id, watch_time, completed FROM watch_history;
```

## 10. Integration Testing

### End-to-End Flow

1. Register new user
2. Become a creator
3. Upload a video
4. Wait for processing
5. Play the video
6. Check analytics
7. Another user subscribes
8. Check subscriber count

### Service Communication

Check logs for inter-service communication:
```powershell
# Django to PostgreSQL
docker-compose logs django | Select-String "database"

# FastAPI to MinIO
docker-compose logs fastapi | Select-String "minio"

# Celery to Redis
docker-compose logs celery_worker | Select-String "redis"
```

## 11. Security Testing

### Test JWT Expiration

1. Get an access token
2. Wait for expiration (30 minutes)
3. Try using expired token
4. Should require refresh token

### Test CORS

Try accessing API from different origin:
```javascript
fetch('http://localhost:8000/api/auth/profile/', {
  headers: {
    'Authorization': 'Bearer token'
  }
})
```

Should allow configured origins only.

### Test Rate Limiting

Make rapid requests to test rate limiting:
```powershell
for ($i=1; $i -le 100; $i++) {
  curl http://localhost:8080/api/videos/
}
```

Should eventually return 429 Too Many Requests.

## 12. Nginx Testing

### Test Reverse Proxy

All these should work:
- http://localhost:8080/api/auth/profile/
- http://localhost:8080/api/videos/
- http://localhost:8080/api/upload/
- http://localhost:8080/videos/1/master.m3u8

### Test Static Files

Check if static files are served:
- http://localhost:8080/static/
- http://localhost:8080/media/

### Test Health Check

```powershell
curl http://localhost:8080/health
```

Should return "healthy".

## 13. Troubleshooting Tests

If something doesn't work:

### Check Service Status
```powershell
docker-compose ps
```

### View Service Logs
```powershell
docker-compose logs <service-name>
```

### Restart Service
```powershell
docker-compose restart <service-name>
```

### Check Network
```powershell
docker network ls
docker network inspect ai-writer_video_network
```

### Check Volumes
```powershell
docker volume ls
docker volume inspect ai-writer_postgres_data
```

## 14. Automated Testing

### Django Tests

```powershell
docker-compose exec django python manage.py test
```

### FastAPI Tests

```powershell
docker-compose exec fastapi pytest
```

## Test Checklist

- [ ] User registration works
- [ ] User login works
- [ ] JWT tokens are generated
- [ ] Token refresh works
- [ ] Video upload completes
- [ ] Video processing succeeds
- [ ] All quality levels are generated
- [ ] Thumbnail is created
- [ ] Files are uploaded to MinIO
- [ ] Video playback works
- [ ] HLS streaming is smooth
- [ ] Quality switching works
- [ ] Watch progress is tracked
- [ ] Analytics are calculated
- [ ] Subscriptions work
- [ ] Creator dashboard shows data
- [ ] Error handling works
- [ ] Security measures are active
- [ ] All services are healthy
- [ ] Database queries work
- [ ] Nginx proxying works

## Performance Benchmarks

**Expected Performance:**
- Video upload: Depends on file size and network
- Video encoding: 2-5x video duration
- API response time: < 200ms
- HLS segment loading: < 100ms
- Database queries: < 50ms

**Resource Usage:**
- PostgreSQL: ~100-200MB RAM
- Redis: ~50MB RAM
- MinIO: ~100MB RAM
- Django: ~200-300MB RAM
- FastAPI: ~200-300MB RAM
- Celery worker: ~300-500MB RAM
- Nginx: ~50MB RAM
- Frontend: ~100MB RAM

Total: ~1.5-2GB RAM for all services.

## Success Criteria

✅ All services start without errors
✅ User can register and login
✅ Video can be uploaded successfully
✅ Video is encoded to all quality levels
✅ Video can be played back smoothly
✅ Analytics are tracked correctly
✅ All API endpoints respond correctly
✅ No security vulnerabilities found
✅ System handles errors gracefully
✅ Performance is acceptable

If all tests pass, the system is working correctly! 🎉
