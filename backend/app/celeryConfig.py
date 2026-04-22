from dotenv import load_dotenv
from celery.schedules import crontab
import os

load_dotenv()


broker_url = os.getenv('BROKER_URL') or os.getenv('broker_url') or 'redis://localhost:6379/0'
result_backend = os.getenv('RESULT_BACKEND') or os.getenv('result_backend') or 'redis://localhost:6379/0'
broker_connection_retry_on_startup = True
timezone='UTC'
task_serializer='json'
accept_content=['json']
result_serializer='json'
enable_utc=True
imports = ('app.tasks.application_tasks',)
beat_schedule = {
#         # # Daily Reminder - Runs every day at 8:00 AM
#         # 'send-daily-reminders': {
#         #     'task': 'tasks.send_daily_reminders',
#         #     'schedule': crontab(hour=16, minute=30),
#         # },
#         # # Monthly Report - Runs on the 1st of every month at 9:00 AM
#         # 'send-monthly-report': {
#         #     'task': 'tasks.send_monthly_report',
#         #     'schedule': crontab(minute=0, hour=9, day_of_month=1, month_of_year='*'),
#         # },
#         # 'cleanup-expired-tokens': {
#         #     'task': 'tasks.cleanup_expired_tokens',
#         #     'schedule': crontab(hour=2, minute=30, day_of_week=0),  # Sunday
#         # },
    }