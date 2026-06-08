from flask_restx import fields

class EventModels:
    def __init__(self, api):
        self.event_post = ns = api # store api reference as ns
        
        self.event_post = api.model('EventPost', {
            'title': fields.String(required=True, description='Event Title'),
            'description': fields.String(description='Event Description'),
            'event_date': fields.DateTime(required=True, description='Event Date and Time'),
            'event_type': fields.String(required=True, description='Event Type (e.g. meeting, occasion, ceremony)'),
            'location': fields.String(description='Event Location')
        })
        
        self.event_response = api.model('EventResponse', {
            'id': fields.Integer(description='Event ID'),
            'title': fields.String(description='Event Title'),
            'description': fields.String(description='Event Description'),
            'event_date': fields.String(description='Event Date and Time'),
            'event_type': fields.String(description='Event Type'),
            'location': fields.String(description='Event Location'),
            'created_at': fields.String(description='Created At'),
            'updated_at': fields.String(description='Updated At')
        })
        
        self.events_list_response = api.model('EventsListResponse', {
            'success': fields.Boolean(description='Success status'),
            'message': fields.String(description='Message'),
            'data': fields.List(fields.Nested(self.event_response), description='List of events')
        })

        self.generic_response = api.model('EventGenericResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Raw
        })
