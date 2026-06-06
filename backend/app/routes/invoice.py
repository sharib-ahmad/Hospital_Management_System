from flask_restx import Namespace, Resource
from ..services.invoice import InvoiceService
from ..utils.role import role_required
from ..utils.enum import UserRole
from flask_jwt_extended import current_user

invoice_ns = Namespace('invoices', description='Consolidated billing operations')

@invoice_ns.route('')
class MyInvoices(Resource):
    @invoice_ns.doc('get_my_invoices', security='Bearer Auth')
    @role_required(UserRole.USER)
    def get(self):
        """Retrieve invoices for all patient profiles registered under the user"""
        return InvoiceService.get_my_invoices(current_user.id)

@invoice_ns.route('/all')
class AllInvoices(Resource):
    @invoice_ns.doc('get_all_invoices', security='Bearer Auth')
    @role_required(UserRole.ADMIN, UserRole.PHARMACIST)
    def get(self):
        """Retrieve all invoices in the system (Admin/Pharmacist only)"""
        return InvoiceService.get_all_invoices()

@invoice_ns.route('/<string:invoice_id>/pay')
@invoice_ns.param('invoice_id', 'The invoice UUID')
class PayInvoice(Resource):
    @invoice_ns.doc('pay_invoice', security='Bearer Auth')
    @role_required(UserRole.USER)
    def post(self, invoice_id):
        """Simulate paying an invoice"""
        return InvoiceService.pay_invoice(invoice_id)
