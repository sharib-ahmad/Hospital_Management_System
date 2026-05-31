from ..extensions import db
from ..utils.time import utc_now
import uuid
import enum

class PharmacyOrderStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    manufacturer = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    __table_args__ = (
        db.CheckConstraint('price >= 0', name='check_medicine_price_non_negative'),
        db.CheckConstraint('stock >= 0', name='check_medicine_stock_non_negative'),
    )

    def __repr__(self):
        return f"<Medicine {self.name} - Stock: {self.stock}>"

class PharmacyOrder(db.Model):
    __tablename__ = 'pharmacy_orders'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('patients.id'), nullable=True)
    order_date = db.Column(db.DateTime, default=utc_now, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(PharmacyOrderStatus, name="pharmacy_order_status"), default=PharmacyOrderStatus.PENDING, nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = db.relationship('User', lazy='joined')
    patient = db.relationship('Patient', lazy='joined')
    items = db.relationship('PharmacyOrderItem', back_populates='order', cascade='all, delete-orphan', lazy='joined')

    def __repr__(self):
        return f"<PharmacyOrder {self.id} - Status: {self.status.value}>"

class PharmacyOrderItem(db.Model):
    __tablename__ = 'pharmacy_order_items'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('pharmacy_orders.id'), nullable=False)
    medicine_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    order = db.relationship('PharmacyOrder', back_populates='items')
    medicine = db.relationship('Medicine', lazy='joined')

    def __repr__(self):
        return f"<PharmacyOrderItem {self.id} - Medicine: {self.medicine_id} x{self.quantity}>"
