from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from ..controllers.appointment_controller import AppointmentController
from ..api_models.appointment_models import AppointmentModels

appointment_ns = Namespace('appointments', description='Appointment management operations')
appointment_models = AppointmentModels(appointment_ns)

@appointment_ns.route('')
class AppointmentList(Resource):
    @appointment_ns.doc('list_appointments', security='Bearer Auth')
    @appointment_ns.marshal_with(appointment_models.response_list_model)
    @jwt_required()
    def get(self):
        """List all appointments for the current user"""
        return AppointmentController.get_appointments()

    @appointment_ns.doc('create_appointment', security='Bearer Auth')
    @appointment_ns.expect(appointment_models.appointment_create)
    @appointment_ns.marshal_with(appointment_models.response_model)
    @jwt_required()
    def post(self):
        """Book a new appointment"""
        return AppointmentController.create_appointment(appointment_ns.payload)

@appointment_ns.route('/<string:appointment_id>')
@appointment_ns.param('appointment_id', 'The appointment identifier')
class AppointmentDetail(Resource):
    @appointment_ns.doc('get_appointment', security='Bearer Auth')
    @appointment_ns.marshal_with(appointment_models.response_model)
    @jwt_required()
    def get(self, appointment_id):
        """Fetch an appointment by ID"""
        return AppointmentController.get_appointment(appointment_id)

    @appointment_ns.doc('update_appointment', security='Bearer Auth')
    @appointment_ns.expect(appointment_models.appointment_update)
    @appointment_ns.marshal_with(appointment_models.response_model)
    @jwt_required()
    def put(self, appointment_id):
        """Update appointment status or details"""
        return AppointmentController.update_appointment(appointment_id, appointment_ns.payload)
