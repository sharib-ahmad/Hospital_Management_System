from flask import Flask
from .config import config_dict
from .extensions import db, jwt

def create_appp(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    db.init_app(app)
    jwt.init_app(app)
    
    return app
