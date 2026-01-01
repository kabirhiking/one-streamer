# Test Video Upload Script
# This script registers a user, logs in, and uploads a video

$DJANGO_API = "http://localhost:8000"
$VIDEO_API = "http://localhost:8001"

Write-Host "=== Video Upload Test Script ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Register a new user
Write-Host "Step 1: Registering user..." -ForegroundColor Yellow
$registerBody = @{
    email = "testuser@example.com"
    password = "testpass123"
    password2 = "testpass123"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$DJANGO_API/api/auth/register/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $registerBody `
        -ErrorAction SilentlyContinue
    Write-Host "✓ Registration successful!" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ User already exists (that's OK)" -ForegroundColor Green
    } else {
        Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Step 2: Login to get JWT token
Write-Host "Step 2: Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "testuser@example.com"
    password = "testpass123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$DJANGO_API/api/auth/login/" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    $accessToken = $loginResponse.access
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Access Token: $($accessToken.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Upload a video
Write-Host "Step 3: Preparing to upload video..." -ForegroundColor Yellow
Write-Host "Please enter the path to your video file:"
Write-Host "(Example: C:\Users\YourName\Videos\test.mp4)" -ForegroundColor Gray
$videoPath = Read-Host "Video file path"

if (-not (Test-Path $videoPath)) {
    Write-Host "✗ File not found: $videoPath" -ForegroundColor Red
    exit 1
}

Write-Host "Uploading video..." -ForegroundColor Yellow

# Create multipart form data
$fileBin = [System.IO.File]::ReadAllBytes($videoPath)
$fileName = Split-Path $videoPath -Leaf
$boundary = [System.Guid]::NewGuid().ToString()

$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"title`"",
    "",
    "Test Video Upload",
    "--$boundary",
    "Content-Disposition: form-data; name=`"description`"",
    "",
    "This is a test video uploaded via PowerShell",
    "--$boundary",
    "Content-Disposition: form-data; name=`"visibility`"",
    "",
    "public",
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: video/mp4",
    ""
)

$bodyString = $bodyLines -join "`r`n"
$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyString)
$bodyBytes += $fileBin
$bodyBytes += [System.Text.Encoding]::UTF8.GetBytes("`r`n--$boundary--`r`n")

try {
    $uploadResponse = Invoke-RestMethod -Uri "$VIDEO_API/api/upload/" `
        -Method Post `
        -Headers @{
            "Authorization" = "Bearer $accessToken"
        } `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyBytes
    
    Write-Host "✓ Upload successful!" -ForegroundColor Green
    Write-Host "  Video ID: $($uploadResponse.video_id)" -ForegroundColor Gray
    Write-Host "  Task ID: $($uploadResponse.task_id)" -ForegroundColor Gray
    Write-Host "  Message: $($uploadResponse.message)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Check Celery logs to see video processing:" -ForegroundColor Yellow
Write-Host "docker compose logs -f celery_worker" -ForegroundColor Gray
