# Quick Start Script for Video Streaming Platform
# Run this script to set up and start the application

Write-Host "Video Streaming Platform - Quick Start" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Yellow
docker-compose exec -T django python manage.py migrate

Write-Host ""
Write-Host "Creating superuser..." -ForegroundColor Yellow
Write-Host "Please enter admin credentials:" -ForegroundColor Cyan
docker-compose exec django python manage.py createsuperuser

Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  Django Admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host "  API Docs:     http://localhost:8001/docs" -ForegroundColor White
Write-Host "  MinIO:        http://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "MinIO Credentials:" -ForegroundColor Cyan
Write-Host "  Username: minioadmin" -ForegroundColor White
Write-Host "  Password: minioadmin123" -ForegroundColor White
Write-Host ""
Write-Host "To view logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "To stop: docker-compose down" -ForegroundColor Yellow
Write-Host ""
