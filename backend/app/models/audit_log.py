from ..extensions import db
from ..utils.time import utc_now
import uuid

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON-serialized string
    timestamp = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationship to User
    user = db.relationship('User', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': str(self.user_id) if self.user_id else None,
            'user_name': self.user.full_name if self.user else 'System/Unauthenticated',
            'action': self.action,
            'ip_address': self.ip_address,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f"<AuditLog {self.id} - Action: {self.action} - User: {self.user_id}>"
