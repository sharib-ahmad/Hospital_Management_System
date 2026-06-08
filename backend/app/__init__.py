from flask import Flask, request
from flask_cors import CORS
from .config import config_dict
from .extensions import db, jwt, api, celery, cache, socketio
from flask_socketio import join_room, leave_room
from . import security

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    CORS(
        app,
        origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        supports_credentials=True,
    )
    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    cache.init_app(app)
    socketio.init_app(app)

    # Socket.IO Event Handlers
    
    @socketio.on('connect')
    def handle_connect():
        app.logger.info(f"Socket client connected: {request.sid}")

    @socketio.on('join')
    def handle_join(data):
        user_id = data.get('user_id')
        if user_id:
            join_room(str(user_id))
            app.logger.info(f"Socket client {request.sid} joined room: {user_id}")

    @socketio.on('leave')
    def handle_leave(data):
        user_id = data.get('user_id')
        if user_id:
            leave_room(str(user_id))
            app.logger.info(f"Socket client {request.sid} left room: {user_id}")
    
    
    # Initialize Celery
    celery.config_from_object('app.celeryConfig')
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    celery.autodiscover_tasks(['app.tasks'])

    from .routes import register_routes
    register_routes(api)
    
    from .errors.handlers import register_error_handlers
    register_error_handlers(api)
    
    from .adminCommands import register_commands
    register_commands(app)
    
    return app
