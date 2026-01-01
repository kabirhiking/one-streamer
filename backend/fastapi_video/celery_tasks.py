"""
Celery task references (actual tasks are in workers/celery_workers).
"""
from celery import Celery
from config import settings

# Create Celery app
celery_app = Celery('video_tasks', broker=settings.CELERY_BROKER_URL)

# Import task references
process_video_task = celery_app.signature('tasks.process_video')
