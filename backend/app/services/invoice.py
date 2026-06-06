from ..extensions import db
from ..models.invoice import Invoice
from ..models.medistore import PharmacyOrder, PharmacyOrderStatus
from ..models.appointment import Appointment
from ..models.patient import Patient
from ..utils.enum import UserRole
from ..utils.response import handle_response
from flask_jwt_extended import current_user
from datetime import datetime

class InvoiceService:
    @staticmethod
    def get_my_invoices(user_id):
        """
        Retrieves all invoices for patients belonging to user_id.
        """
        # Get patient IDs
        patients = Patient.query.filter_by(user_id=user_id).all()
        patient_ids = [p.id for p in patients]
        
        if not patient_ids:
            return handle_response(success=True, data=[], message="No invoices found")
            
        invoices = Invoice.query.filter(Invoice.patient_id.in_(patient_ids)).order_by(Invoice.created_at.desc()).all()
        
        # Serialize with names
        serialized_invoices = []
        for inv in invoices:
            serialized_invoices.append({
                'id': str(inv.id),
                'patient_name': inv.patient.full_name if inv.patient else 'Unknown',
                'amount': float(inv.amount),
                'status': inv.status,
                'invoice_type': inv.invoice_type,
                'appointment_id': str(inv.appointment_id) if inv.appointment_id else None,
                'order_id': str(inv.order_id) if inv.order_id else None,
                'created_at': inv.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': inv.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return handle_response(success=True, data=serialized_invoices, message="Invoices retrieved successfully")

    @staticmethod
    def get_all_invoices():
        """
        Retrieves all invoices (Admin/Pharmacist/Staff only).
        """
        invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
        
        serialized_invoices = []
        for inv in invoices:
            serialized_invoices.append({
                'id': str(inv.id),
                'patient_name': inv.patient.full_name if inv.patient else 'Unknown',
                'user_name': inv.user.full_name if inv.user else 'Unknown',
                'amount': float(inv.amount),
                'status': inv.status,
                'invoice_type': inv.invoice_type,
                'appointment_id': str(inv.appointment_id) if inv.appointment_id else None,
                'order_id': str(inv.order_id) if inv.order_id else None,
                'created_at': inv.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': inv.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return handle_response(success=True, data=serialized_invoices, message="All invoices retrieved successfully")

    @staticmethod
    def pay_invoice(invoice_id):
        """
        Simulates payment for an invoice.
        """
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return handle_response(success=False, message="Invoice not found", status_code=404)
            
        # Permission check: patients can only pay their own invoices
        if current_user.role == UserRole.USER:
            patient = Patient.query.filter_by(id=invoice.patient_id, user_id=current_user.id).first()
            if not patient:
                return handle_response(success=False, message="Unauthorized to pay this invoice", status_code=403)
                
        if invoice.status == 'paid':
            return handle_response(success=False, message="Invoice is already paid", status_code=400)
            
        invoice.status = 'paid'
        
        # Trigger follow-up logic based on type
        if invoice.invoice_type == 'pharmacy' and invoice.order_id:
            # Update order status to PROCESSING so pharmacist knows it is paid
            order = PharmacyOrder.query.get(invoice.order_id)
            if order:
                order.status = PharmacyOrderStatus.PROCESSING
                # Trigger email update
                from ..tasks.email_tasks import send_order_status_email
                send_order_status_email.delay(order.id)
                
        # Create In-App Notification
        from .notification import NotificationService
        NotificationService.create_notification(
            user_id=invoice.user_id,
            title="Invoice Paid Successfully",
            message=f"Your payment of ${float(invoice.amount):.2f} for {invoice.invoice_type} services has been processed.",
            category="billing"
        )
        
        db.session.commit()
        return handle_response(success=True, message="Invoice paid successfully")

    @staticmethod
    def create_invoice(patient_id, user_id, amount, invoice_type, appointment_id=None, order_id=None):
        """
        Utility method to create an invoice.
        """
        invoice = Invoice(
            patient_id=patient_id,
            user_id=user_id,
            amount=amount,
            invoice_type=invoice_type,
            appointment_id=appointment_id,
            order_id=order_id,
            status='unpaid'
        )
        db.session.add(invoice)
        db.session.commit()
        
        # Trigger In-App Notification
        from .notification import NotificationService
        NotificationService.create_notification(
            user_id=user_id,
            title="New Invoice Generated",
            message=f"A new invoice of ${float(amount):.2f} has been generated for your {invoice_type} transaction.",
            category="billing"
        )
        return invoice
