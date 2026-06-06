# app/api_models/medistore_models.py
from flask_restx import fields
from ..utils.enum import EnumField
from ..models.medistore import PharmacyOrderStatus

class MediStoreModels:
    def __init__(self, api):
        # Medicine models
        self.medicine = api.model('Medicine', {
            'id': fields.String,
            'name': fields.String,
            'description': fields.String,
            'price': fields.Float,
            'stock': fields.Integer,
            'category': fields.String,
            'manufacturer': fields.String,
            'created_at': fields.DateTime,
            'updated_at': fields.DateTime
        })

        self.medicine_create = api.model('MedicineCreate', {
            'name': fields.String(required=True),
            'description': fields.String,
            'price': fields.Float(required=True),
            'stock': fields.Integer(required=True),
            'category': fields.String(required=True),
            'manufacturer': fields.String
        })

        # Order models
        self.order_item = api.model('OrderItem', {
            'id': fields.String,
            'medicine_id': fields.String,
            'medicine_name': fields.String(attribute='medicine.name'),
            'quantity': fields.Integer,
            'price': fields.Float
        })

        self.order = api.model('PharmacyOrder', {
            'id': fields.String,
            'user_id': fields.String,
            'patient_id': fields.String,
            'order_date': fields.DateTime,
            'total_price': fields.Float,
            'status': EnumField(PharmacyOrderStatus),
            'shipping_address': fields.String,
            'phone_number': fields.String,
            'created_at': fields.DateTime,
            'updated_at': fields.DateTime,
            'patient_name': fields.String(attribute='patient.full_name', skip_none=True),
            'user_name': fields.String(attribute='user.full_name'),
            'items': fields.List(fields.Nested(self.order_item))
        })

        self.cart_item_input = api.model('CartItemInput', {
            'medicine_id': fields.String(required=True),
            'quantity': fields.Integer(required=True)
        })

        self.order_create = api.model('OrderCreate', {
            'patient_id': fields.String,
            'shipping_address': fields.String(required=True),
            'phone_number': fields.String(required=True),
            'items': fields.List(fields.Nested(self.cart_item_input), required=True)
        })

        self.order_status_update = api.model('OrderStatusUpdate', {
            'status': EnumField(PharmacyOrderStatus, required=True)
        })

        # Generic Response models
        self.medicine_list_response = api.model('MedicineListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.medicine))
        })

        self.medicine_response = api.model('MedicineResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.medicine)
        })

        self.order_response = api.model('OrderResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Nested(self.order)
        })

        self.order_list_response = api.model('OrderListResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.List(fields.Nested(self.order))
        })

        self.generic_response = api.model('PharmacyGenericResponse', {
            'success': fields.Boolean,
            'message': fields.String,
            'data': fields.Raw
        })
