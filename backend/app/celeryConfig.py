from dotenv import load_dotenv
from celery.schedules import crontab
import os

load_dotenv()


broker_url = os.getenv('BROKER_URL') or os.getenv('broker_url') or 'redis://localhost:6379/0'
result_backend = os.getenv('RESULT_BACKEND') or os.getenv('result_backend') or 'redis://localhost:6379/0'
broker_connection_retry_on_startup = True
timezone = 'Asia/Kolkata'
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
enable_utc = False
imports = ('app.tasks.application_tasks', 'app.tasks.email_tasks', 'app.tasks.cleanup_tasks')
beat_schedule = {
    'send-daily-agenda': {
        'task': 'app.tasks.email_tasks.send_daily_agenda_emails',
        'schedule': crontab(hour=8, minute=0),
    },
    'cleanup-expired-tokens': {
        'task': 'app.tasks.cleanup_tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),
    },
    'cleanup-old-applications': {
        'task': 'app.tasks.cleanup_tasks.cleanup_old_applications',
        'schedule': crontab(hour=2, minute=30),
    },
}