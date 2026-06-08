import sys
from app import create_app
from app.extensions import db, socketio

app = create_app("development")

if __name__ == "__main__":
    with app.app_context():
        # Create database tables for development if they don't exist
        db.create_all()
    
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
