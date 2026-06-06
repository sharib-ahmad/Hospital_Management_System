from ..extensions import db, celery
from celery import shared_task
from ..models import TokenBlocklist, Application
from ..utils.enum import ApplicationStatus
from datetime import datetime, timedelta

@shared_task(name='app.tasks.cleanup_tasks.cleanup_expired_tokens')
def cleanup_expired_tokens():
    """
    Deletes tokens from TokenBlocklist older than 30 days.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        deleted_count = TokenBlocklist.query.filter(TokenBlocklist.created_at < cutoff).delete()
        db.session.commit()
        return f"Successfully cleaned up {deleted_count} expired blocklist tokens."
    except Exception as e:
        db.session.rollback()
        return f"Failed to cleanup expired tokens: {str(e)}"

@shared_task(name='app.tasks.cleanup_tasks.cleanup_old_applications')
def cleanup_old_applications():
    """
    Deletes APPROVED and REJECTED applications older than 30 days.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        deleted_count = Application.query.filter(
            Application.status.in_([ApplicationStatus.APPROVED, ApplicationStatus.REJECTED]),
            Application.updated_at < cutoff
        ).delete()
        db.session.commit()
        return f"Successfully cleaned up {deleted_count} old approved/rejected applications."
    except Exception as e:
        db.session.rollback()
        return f"Failed to cleanup old applications: {str(e)}"
