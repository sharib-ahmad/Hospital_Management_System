from ..extensions import db
from ..utils.time import utc_now

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'appointment', 'billing', 'order', 'application', 'vitals'
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = db.relationship('User', lazy='joined')

    def __repr__(self):
        return f"<Notification {self.id} - User: {self.user_id} - IsRead: {self.is_read}>"
