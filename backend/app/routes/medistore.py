# app/routes/medistore.py
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from ..controllers.medistore_controller import PharmacyController
from ..api_models.medistore_models import MediStoreModels
from ..utils.role import role_required
from ..utils.enum import UserRole

medistore_ns = Namespace('medistore', description='Pharmacy and Medical Store operations')
medistore_models = MediStoreModels(medistore_ns)

@medistore_ns.route('/medicines')
class MedicineList(Resource):
    @medistore_ns.doc('list_medicines')
    @medistore_ns.marshal_with(medistore_models.medicine_list_response)
    def get(self):
        """List all available medicines"""
        return PharmacyController.get_medicines()

    @medistore_ns.doc('create_medicine', security='Bearer Auth')
    @medistore_ns.expect(medistore_models.medicine_create)
    @medistore_ns.marshal_with(medistore_models.medicine_response)
    @role_required(UserRole.PHARMACIST)
    def post(self):
        """Add a new medicine to inventory (Pharmacist only)"""
        return PharmacyController.create_medicine()

@medistore_ns.route('/medicines/<string:medicine_id>')
@medistore_ns.param('medicine_id', 'The medicine ID')
class MedicineDetail(Resource):
    @medistore_ns.doc('update_medicine', security='Bearer Auth')
    @medistore_ns.expect(medistore_models.medicine_create)
    @medistore_ns.marshal_with(medistore_models.medicine_response)
    @role_required(UserRole.PHARMACIST)
    def put(self, medicine_id):
        """Update a medicine (Pharmacist only)"""
        return PharmacyController.update_medicine(medicine_id)

    @medistore_ns.doc('delete_medicine', security='Bearer Auth')
    @medistore_ns.marshal_with(medistore_models.generic_response)
    @role_required(UserRole.PHARMACIST)
    def delete(self, medicine_id):
        """Delete a medicine (Pharmacist only)"""
        return PharmacyController.delete_medicine(medicine_id)

@medistore_ns.route('/orders/my')
class MyOrderList(Resource):
    @medistore_ns.doc('list_my_orders', security='Bearer Auth')
    @medistore_ns.marshal_with(medistore_models.order_list_response)
    @role_required(UserRole.USER)
    def get(self):
        """List all pharmacy orders placed by the current user"""
        return PharmacyController.get_my_orders()

@medistore_ns.route('/orders/all')
class AllOrderList(Resource):
    @medistore_ns.doc('list_all_orders', security='Bearer Auth')
    @medistore_ns.marshal_with(medistore_models.order_list_response)
    @role_required(UserRole.PHARMACIST)
    def get(self):
        """List all pharmacy orders (Pharmacist only)"""
        return PharmacyController.get_all_orders()

@medistore_ns.route('/orders')
class OrderCreate(Resource):
    @medistore_ns.doc('create_order', security='Bearer Auth')
    @medistore_ns.expect(medistore_models.order_create)
    @medistore_ns.marshal_with(medistore_models.order_response)
    @role_required(UserRole.USER)
    def post(self):
        """Place a new pharmacy order"""
        return PharmacyController.create_order()

@medistore_ns.route('/orders/<string:order_id>/status')
@medistore_ns.param('order_id', 'The pharmacy order UUID')
class OrderStatusUpdate(Resource):
    @medistore_ns.doc('update_order_status', security='Bearer Auth')
    @medistore_ns.expect(medistore_models.order_status_update)
    @medistore_ns.marshal_with(medistore_models.order_response)
    @role_required(UserRole.PHARMACIST)
    def put(self, order_id):
        """Update a pharmacy order's processing/delivery status (Pharmacist only)"""
        return PharmacyController.update_order_status(order_id)
