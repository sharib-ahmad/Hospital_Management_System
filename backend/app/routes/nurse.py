# app/routes/nurse.py
from flask_restx import Namespace, Resource
from ..api_models.nurse_models import NurseModels
from ..controllers.nurse_controller import NurseController
from ..utils.role import role_required
from ..utils.enum import UserRole

nurse_ns = Namespace('nurses', description='Nurse operations')
nurse_models = NurseModels(nurse_ns)

@nurse_ns.route('/')
class NurseList(Resource):
    @nurse_ns.doc(params={'department_id': 'Filter by department ID'})
    @nurse_ns.marshal_with(nurse_models.nurse_list_response)
    def get(self):
        """List all nurses"""
        return NurseController.get_nurses()

@nurse_ns.route('/<string:nurse_code>')
@nurse_ns.param('nurse_code', 'The nurse code')
class NurseDetail(Resource):
    @nurse_ns.marshal_with(nurse_models.nurse_response)
    def get(self, nurse_code):
        """Get nurse details"""
        return NurseController.get_nurse(nurse_code)

    @role_required(UserRole.ADMIN, UserRole.NURSE)
    @nurse_ns.expect(nurse_models.nurse_base)
    @nurse_ns.marshal_with(nurse_models.nurse_response)
    def put(self, nurse_code):
        """Update nurse details (Admin or own Nurse profile)"""
        return NurseController.update_nurse(nurse_code)
