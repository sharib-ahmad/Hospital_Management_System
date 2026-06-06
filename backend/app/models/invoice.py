from ..extensions import db
from ..utils.time import utc_now
import uuid

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=False)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    
    appointment_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('appointments.id'), nullable=True)
    order_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('pharmacy_orders.id'), nullable=True)
    
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='unpaid', nullable=False) # 'unpaid', 'paid', 'refunded'
    invoice_type = db.Column(db.String(30), nullable=False) # 'consultation', 'pharmacy'
    
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    patient = db.relationship('Patient', lazy='joined')
    user = db.relationship('User', lazy='joined')
    appointment = db.relationship('Appointment', lazy='joined')
    order = db.relationship('PharmacyOrder', lazy='joined')

    def __repr__(self):
        return f"<Invoice {self.id} - Amount: {self.amount} - Status: {self.status}>"
