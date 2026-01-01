# Video Streaming Platform - Helper Commands
# This file contains common commands for managing the platform

function Show-Help {
    Write-Host ""
    Write-Host "Video Streaming Platform - Helper Commands" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: . .\commands.ps1; <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available Commands:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Start-Platform        - Start all services" -ForegroundColor White
    Write-Host "  Stop-Platform         - Stop all services" -ForegroundColor White
    Write-Host "  Restart-Platform      - Restart all services" -ForegroundColor White
    Write-Host "  Show-Status           - Show status of all services" -ForegroundColor White
    Write-Host "  Show-Logs             - Show logs from all services" -ForegroundColor White
    Write-Host "  Clean-Platform        - Stop and remove all containers and volumes" -ForegroundColor White
    Write-Host ""
    Write-Host "  Run-Migrations        - Run Django database migrations" -ForegroundColor White
    Write-Host "  Create-Superuser      - Create Django admin user" -ForegroundColor White
    Write-Host "  Django-Shell          - Open Django shell" -ForegroundColor White
    Write-Host "  Database-Shell        - Open PostgreSQL shell" -ForegroundColor White
    Write-Host ""
    Write-Host "  Test-Django           - Run Django tests" -ForegroundColor White
    Write-Host "  Test-FastAPI          - Run FastAPI tests" -ForegroundColor White
    Write-Host ""
    Write-Host "  Show-URLs             - Display all application URLs" -ForegroundColor White
    Write-Host "  Check-Health          - Check health of all services" -ForegroundColor White
    Write-Host ""
}

function Start-Platform {
    Write-Host "Starting Video Streaming Platform..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "✓ Platform started" -ForegroundColor Green
    Show-URLs
}

function Stop-Platform {
    Write-Host "Stopping Video Streaming Platform..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✓ Platform stopped" -ForegroundColor Green
}

function Restart-Platform {
    Write-Host "Restarting Video Streaming Platform..." -ForegroundColor Yellow
    docker-compose restart
    Write-Host "✓ Platform restarted" -ForegroundColor Green
}

function Show-Status {
    Write-Host "Service Status:" -ForegroundColor Cyan
    docker-compose ps
}

function Show-Logs {
    param(
        [string]$Service = ""
    )
    if ($Service) {
        docker-compose logs -f $Service
    } else {
        docker-compose logs -f
    }
}

function Clean-Platform {
    Write-Host "WARNING: This will remove all containers and data!" -ForegroundColor Red
    $confirm = Read-Host "Are you sure? (yes/no)"
    if ($confirm -eq "yes") {
        Write-Host "Cleaning up..." -ForegroundColor Yellow
        docker-compose down -v
        Write-Host "✓ Cleanup complete" -ForegroundColor Green
    } else {
        Write-Host "Cancelled" -ForegroundColor Yellow
    }
}

function Run-Migrations {
    Write-Host "Running database migrations..." -ForegroundColor Yellow
    docker-compose exec django python manage.py makemigrations
    docker-compose exec django python manage.py migrate
    Write-Host "✓ Migrations complete" -ForegroundColor Green
}

function Create-Superuser {
    Write-Host "Creating Django superuser..." -ForegroundColor Yellow
    docker-compose exec django python manage.py createsuperuser
}

function Django-Shell {
    Write-Host "Opening Django shell..." -ForegroundColor Yellow
    docker-compose exec django python manage.py shell
}

function Database-Shell {
    Write-Host "Opening PostgreSQL shell..." -ForegroundColor Yellow
    docker-compose exec postgres psql -U postgres -d video_streaming_db
}

function Test-Django {
    Write-Host "Running Django tests..." -ForegroundColor Yellow
    docker-compose exec django python manage.py test
}

function Test-FastAPI {
    Write-Host "Running FastAPI tests..." -ForegroundColor Yellow
    docker-compose exec fastapi pytest
}

function Show-URLs {
    Write-Host ""
    Write-Host "Application URLs:" -ForegroundColor Cyan
    Write-Host "  Frontend:     http://localhost:3000" -ForegroundColor White
    Write-Host "  Django Admin: http://localhost:8000/admin" -ForegroundColor White
    Write-Host "  Django API:   http://localhost:8000/api/docs/" -ForegroundColor White
    Write-Host "  FastAPI Docs: http://localhost:8001/docs" -ForegroundColor White
    Write-Host "  Nginx:        http://localhost:8080" -ForegroundColor White
    Write-Host "  MinIO:        http://localhost:9001" -ForegroundColor White
    Write-Host ""
    Write-Host "MinIO Credentials:" -ForegroundColor Cyan
    Write-Host "  Username: minioadmin" -ForegroundColor White
    Write-Host "  Password: minioadmin123" -ForegroundColor White
    Write-Host ""
}

function Check-Health {
    Write-Host "Checking service health..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Django Health: " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Unhealthy" -ForegroundColor Red
    }
    
    Write-Host "FastAPI Health: " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Unhealthy" -ForegroundColor Red
    }
    
    Write-Host "Nginx Health: " -NoNewline
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ Healthy" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ Unhealthy" -ForegroundColor Red
    }
    
    Write-Host ""
}

function Watch-Celery {
    Write-Host "Watching Celery worker logs..." -ForegroundColor Yellow
    docker-compose logs -f celery_worker
}

function Scale-Service {
    param(
        [string]$Service,
        [int]$Count
    )
    Write-Host "Scaling $Service to $Count instances..." -ForegroundColor Yellow
    docker-compose up -d --scale $Service=$Count
    Write-Host "✓ Service scaled" -ForegroundColor Green
}

function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $filename = "backup_$timestamp.sql"
    Write-Host "Creating database backup: $filename" -ForegroundColor Yellow
    docker-compose exec -T postgres pg_dump -U postgres video_streaming_db > $filename
    Write-Host "✓ Backup created: $filename" -ForegroundColor Green
}

function Restore-Database {
    param(
        [string]$BackupFile
    )
    if (Test-Path $BackupFile) {
        Write-Host "Restoring database from: $BackupFile" -ForegroundColor Yellow
        Get-Content $BackupFile | docker-compose exec -T postgres psql -U postgres video_streaming_db
        Write-Host "✓ Database restored" -ForegroundColor Green
    } else {
        Write-Host "✗ Backup file not found: $BackupFile" -ForegroundColor Red
    }
}

# Display help on import
Show-Help

# Export functions
Export-ModuleMember -Function *
