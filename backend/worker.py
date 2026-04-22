from app import create_app
from app.extensions import celery

flask_app = create_app()
# The celery object is already configured in create_app()
