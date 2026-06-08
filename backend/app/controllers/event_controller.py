from flask import request
from ..services.event import EventService
from ..schemas.event import EventCreateSchema
from ..utils.response import handle_response

class EventController:
    @staticmethod
    def get_events():
        return EventService.get_all_events()

    @staticmethod
    def create_event():
        data = request.get_json()
        try:
            validated = EventCreateSchema(**data)
            return EventService.create_event(validated)
        except Exception as e:
            return handle_response(success=False, message=str(e), status_code=400)

    @staticmethod
    def delete_event(event_id):
        return EventService.delete_event(event_id)
