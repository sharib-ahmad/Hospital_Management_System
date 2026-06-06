# app/controllers/medistore_controller.py
from flask import request
from ..services.medistore import PharmacyService
from ..schemas.medistore_schemas import MedicineCreateSchema, OrderCreateSchema, OrderStatusUpdateSchema
from pydantic import ValidationError
from ..utils.response import handle_response
from ..utils.request import validate_json
from flask_jwt_extended import current_user

class PharmacyController:
    @staticmethod
    def get_medicines():
        medicines = PharmacyService.get_all_medicines()
        return handle_response(
            success=True,
            message="Medicines retrieved successfully",
            data=medicines
        )

    @staticmethod
    def create_medicine():
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = MedicineCreateSchema(**data)
            return PharmacyService.create_medicine(validated_data)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def get_my_orders():
        return PharmacyService.get_user_orders(current_user.id)

    @staticmethod
    def get_all_orders():
        return PharmacyService.get_all_orders()

    @staticmethod
    def create_order():
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = OrderCreateSchema(**data)
            return PharmacyService.create_order(current_user.id, validated_data)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def update_order_status(order_id):
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = OrderStatusUpdateSchema(**data)
            return PharmacyService.update_order_status(order_id, validated_data.status)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def update_medicine(medicine_id):
        data, error = validate_json()
        if error:
            return error
        try:
            validated_data = MedicineCreateSchema(**data)
            return PharmacyService.update_medicine(medicine_id, validated_data)
        except ValidationError as e:
            return handle_response(
                success=False,
                message="Validation Error",
                errors=e.errors(),
                status_code=400
            )

    @staticmethod
    def delete_medicine(medicine_id):
        return PharmacyService.delete_medicine(medicine_id)
