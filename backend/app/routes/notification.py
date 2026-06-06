from flask_restx import Namespace, Resource
from ..services.notification import NotificationService
from ..utils.role import role_required
from ..utils.enum import UserRole
from flask_jwt_extended import current_user

notification_ns = Namespace('notifications', description='In-app notification system operations')

@notification_ns.route('')
class MyNotifications(Resource):
    @notification_ns.doc('get_my_notifications', security='Bearer Auth')
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN, UserRole.PHARMACIST)
    def get(self):
        """Retrieve all notifications for the current authenticated user"""
        return NotificationService.get_my_notifications(current_user.id)

@notification_ns.route('/read-all')
class MarkAllRead(Resource):
    @notification_ns.doc('mark_all_notifications_read', security='Bearer Auth')
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN, UserRole.PHARMACIST)
    def put(self):
        """Mark all unread notifications for the user as read"""
        return NotificationService.mark_all_as_read(current_user.id)

@notification_ns.route('/<int:notification_id>/read')
@notification_ns.param('notification_id', 'The notification ID')
class MarkRead(Resource):
    @notification_ns.doc('mark_notification_read', security='Bearer Auth')
    @role_required(UserRole.USER, UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN, UserRole.PHARMACIST)
    def put(self, notification_id):
        """Mark a single notification as read"""
        return NotificationService.mark_as_read(notification_id, current_user.id)
