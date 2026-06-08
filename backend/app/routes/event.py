from flask_restx import Namespace, Resource
from ..api_models.event_model import EventModels
from ..controllers.event_controller import EventController
from ..utils.role import role_required
from ..utils.enum import UserRole

event_ns = Namespace('events', description='Event related operations')
event_models = EventModels(event_ns)

@event_ns.route('')
class EventList(Resource):
    @event_ns.marshal_with(event_models.events_list_response)
    def get(self):
        """List all events"""
        return EventController.get_events()

    @role_required(UserRole.ADMIN)
    @event_ns.expect(event_models.event_post)
    @event_ns.marshal_with(event_models.events_list_response)
    def post(self):
        """Create a new event (Admin only)"""
        return EventController.create_event()


@event_ns.route('/<int:event_id>')
class EventDetail(Resource):
    @role_required(UserRole.ADMIN)
    @event_ns.marshal_with(event_models.generic_response)
    def delete(self, event_id):
        """Delete an event (Admin only)"""
        return EventController.delete_event(event_id)
