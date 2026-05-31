from flask import Flask
from flask_cors import CORS
from .config import config_dict
from .extensions import db, jwt, api, celery, cache
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
