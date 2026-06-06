from ..extensions import db
from ..models.notification import Notification
from ..utils.response import handle_response

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, category):
        """
        Creates an in-app notification.
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            category=category,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_my_notifications(user_id):
        """
        Retrieves all notifications for user_id.
        """
        notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
        
        serialized = []
        for n in notifications:
            serialized.append({
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'is_read': n.is_read,
                'category': n.category,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return handle_response(success=True, data=serialized, message="Notifications retrieved successfully")

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """
        Marks a specific notification as read.
        """
        n = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if not n:
            return handle_response(success=False, message="Notification not found", status_code=404)
            
        n.is_read = True
        db.session.commit()
        return handle_response(success=True, message="Notification marked as read")

    @staticmethod
    def mark_all_as_read(user_id):
        """
        Marks all unread notifications for user as read.
        """
        Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
        db.session.commit()
        return handle_response(success=True, message="All notifications marked as read")
