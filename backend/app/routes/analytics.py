from flask_restx import Namespace, Resource
from ..services.analytics import AnalyticsService
from ..utils.role import role_required
from ..utils.enum import UserRole

analytics_ns = Namespace('analytics', description='Dashboard analytics operations')

@analytics_ns.route('/admin')
class AdminAnalytics(Resource):
    @analytics_ns.doc('get_admin_analytics', security='Bearer Auth')
    @role_required(UserRole.ADMIN)
    def get(self):
        """Retrieve hospital administrative analytics (revenue, patient volume)"""
        return AnalyticsService.get_admin_analytics()

@analytics_ns.route('/doctor')
class DoctorAnalytics(Resource):
    @analytics_ns.doc('get_doctor_analytics', security='Bearer Auth')
    @role_required(UserRole.DOCTOR)
    def get(self):
        """Retrieve doctor clinical analytics (trends, common diagnoses, slot stats)"""
        return AnalyticsService.get_doctor_analytics()
