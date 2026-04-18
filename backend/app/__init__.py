from flask import Flask
from flask_cors import CORS
from .config import config_dict
from .extensions import db, jwt, api
from . import security

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)

    from .routes import register_routes
    register_routes(api)
    
    from .adminCommands import register_commands
    register_commands(app)
    
    return app
