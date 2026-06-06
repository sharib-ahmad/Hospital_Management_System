from flask_restx import Namespace, Resource
from ..api_models.pharmacist_models import PharmacistModels
from ..controllers.pharmacist_controller import PharmacistController
from ..utils.role import role_required
from ..utils.enum import UserRole

pharmacist_ns = Namespace('pharmacists', description='Pharmacist operations')
pharmacist_models = PharmacistModels(pharmacist_ns)

@pharmacist_ns.route('/')
class PharmacistList(Resource):
    @pharmacist_ns.doc(params={'department_id': 'Filter by department ID'})
    @pharmacist_ns.marshal_with(pharmacist_models.pharmacist_list_response)
    def get(self):
        """List all pharmacists"""
        return PharmacistController.get_pharmacists()

@pharmacist_ns.route('/me')
class PharmacistMe(Resource):
    @pharmacist_ns.doc('get_my_pharmacist_profile', security='Bearer Auth')
    @pharmacist_ns.marshal_with(pharmacist_models.pharmacist_response)
    @role_required(UserRole.PHARMACIST)
    def get(self):
        """Get the current pharmacist's own profile"""
        return PharmacistController.get_me()

    @pharmacist_ns.doc('update_my_pharmacist_profile', security='Bearer Auth')
    @pharmacist_ns.expect(pharmacist_models.pharmacist_base)
    @pharmacist_ns.marshal_with(pharmacist_models.pharmacist_response)
    @role_required(UserRole.PHARMACIST)
    def put(self):
        """Update the current pharmacist's own profile"""
        return PharmacistController.update_me()

@pharmacist_ns.route('/<string:pharmacist_code>')
@pharmacist_ns.param('pharmacist_code', 'The pharmacist code')
class PharmacistDetail(Resource):
    @pharmacist_ns.marshal_with(pharmacist_models.pharmacist_response)
    def get(self, pharmacist_code):
        """Get pharmacist details"""
        return PharmacistController.get_pharmacist(pharmacist_code)

    @role_required(UserRole.ADMIN, UserRole.PHARMACIST)
    @pharmacist_ns.expect(pharmacist_models.pharmacist_base)
    @pharmacist_ns.marshal_with(pharmacist_models.pharmacist_response)
    def put(self, pharmacist_code):
        """Update pharmacist details (Admin or own Pharmacist profile)"""
        return PharmacistController.update_pharmacist(pharmacist_code)
