# app/services/medistore.py
from ..extensions import db
from ..models.medistore import Medicine, PharmacyOrder, PharmacyOrderItem, PharmacyOrderStatus
from ..models.patient import Patient
from ..utils.response import handle_response
from decimal import Decimal

class PharmacyService:
    @staticmethod
    def get_all_medicines():
        return Medicine.query.all()

    @staticmethod
    def create_medicine(data):
        # Prevent duplicates
        existing = Medicine.query.filter_by(name=data.name).first()
        if existing:
            return handle_response(success=False, message=f"Medicine {data.name} already exists", status_code=400)
            
        medicine = Medicine(
            name=data.name,
            description=data.description,
            price=Decimal(data.price),
            stock=data.stock,
            category=data.category,
            manufacturer=data.manufacturer
        )
        db.session.add(medicine)
        db.session.commit()
        return handle_response(success=True, data=medicine, message="Medicine added successfully", status_code=201)

    @staticmethod
    def get_user_orders(user_id):
        orders = PharmacyOrder.query.filter_by(user_id=user_id).order_by(PharmacyOrder.order_date.desc()).all()
        return handle_response(success=True, data=orders, message="Your orders retrieved successfully")

    @staticmethod
    def get_all_orders():
        orders = PharmacyOrder.query.order_by(PharmacyOrder.order_date.desc()).all()
        return handle_response(success=True, data=orders, message="All orders retrieved successfully")

    @staticmethod
    def create_order(user_id, data):
        # Validate patient if provided
        if data.patient_id:
            patient = Patient.query.filter_by(id=data.patient_id, user_id=user_id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized access to this patient profile", status_code=403)

        # Start transaction block
        try:
            total_price = Decimal('0.00')
            order_items = []
            
            # 1. Validate all cart items and stock
            for item in data.items:
                medicine = Medicine.query.get(item.medicine_id)
                if not medicine:
                    db.session.rollback()
                    return handle_response(success=False, message=f"Medicine with ID {item.medicine_id} not found", status_code=404)
                    
                if medicine.stock < item.quantity:
                    db.session.rollback()
                    return handle_response(success=False, message=f"Insufficient stock for {medicine.name}. Available: {medicine.stock}", status_code=400)
                
                # Decrement Stock
                medicine.stock -= item.quantity
                item_price = medicine.price * item.quantity
                total_price += item_price
                
                order_item = PharmacyOrderItem(
                    medicine_id=medicine.id,
                    quantity=item.quantity,
                    price=medicine.price
                )
                order_items.append(order_item)

            # 2. Save Order
            order = PharmacyOrder(
                user_id=user_id,
                patient_id=data.patient_id,
                total_price=total_price,
                status=PharmacyOrderStatus.PENDING,
                shipping_address=data.shipping_address,
                phone_number=data.phone_number
            )
            db.session.add(order)
            db.session.flush() # Populate order ID

            # 3. Save Items
            for item in order_items:
                item.order_id = order.id
                db.session.add(item)
                
            db.session.commit()
            return handle_response(success=True, data=order, message="Pharmacy order placed successfully", status_code=201)

        except Exception as e:
            db.session.rollback()
            return handle_response(success=False, message=f"Failed to place order: {str(e)}", status_code=500)

    @staticmethod
    def update_order_status(order_id, status):
        order = PharmacyOrder.query.get(order_id)
        if not order:
            return handle_response(success=False, message="Order not found", status_code=404)
            
        order.status = status
        db.session.commit()
        return handle_response(success=True, data=order, message="Order status updated successfully")

    @staticmethod
    def update_medicine(medicine_id, data):
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return handle_response(success=False, message="Medicine not found", status_code=404)

        medicine.name = data.name
        medicine.description = data.description
        medicine.price = Decimal(data.price)
        medicine.stock = data.stock
        medicine.category = data.category
        medicine.manufacturer = data.manufacturer

        db.session.commit()
        return handle_response(success=True, data=medicine, message="Medicine updated successfully")

    @staticmethod
    def delete_medicine(medicine_id):
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return handle_response(success=False, message="Medicine not found", status_code=404)

        db.session.delete(medicine)
        db.session.commit()
        return handle_response(success=True, message="Medicine deleted successfully")
