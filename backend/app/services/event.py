from ..extensions import db
from ..models.event import Event
from ..utils.response import handle_response

class EventService:
    @staticmethod
    def get_all_events():
        events = Event.query.order_by(Event.event_date.asc()).all()
        return handle_response(success=True, data=events, message="Events retrieved successfully")

    @staticmethod
    def create_event(data):
        event = Event(
            title=data.title,
            description=data.description,
            event_date=data.event_date,
            event_type=data.event_type,
            location=data.location
        )
        db.session.add(event)
        db.session.commit()
        
        # Trigger Google Chat notification task
        from ..tasks.email_tasks import send_event_creation_notification
        send_event_creation_notification.delay(event.id)
        
        return handle_response(success=True, data=event, message="Event created successfully", status_code=201)

    @staticmethod
    def delete_event(event_id):
        event = Event.query.get(event_id)
        if not event:
            return handle_response(success=False, message="Event not found", status_code=404)
        db.session.delete(event)
        db.session.commit()
        return handle_response(success=True, message="Event deleted successfully")
