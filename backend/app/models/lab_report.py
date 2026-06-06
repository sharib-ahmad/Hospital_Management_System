from ..extensions import db
from ..utils.time import utc_now
import uuid

class LabReport(db.Model):
    __tablename__ = 'lab_reports'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    uploaded_by = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    patient = db.relationship('Patient', lazy='joined')
    uploader = db.relationship('User', lazy='joined')

    def __repr__(self):
        return f"<LabReport {self.id} - Title: {self.title}>"
