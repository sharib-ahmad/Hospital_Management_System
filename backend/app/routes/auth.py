# app/routes/auth.py

from flask import request
from http import HTTPStatus
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from ..utils.role import role_required, UserRole
from ..api_models import AuthModels
from ..controllers.auth_controller import AuthController

auth_ns = Namespace('auth', description='Authentication related operations')

models = AuthModels(auth_ns)


@auth_ns.route('/register')
class Register(Resource):

    @auth_ns.expect(models.register)
    @auth_ns.marshal_with(models.response_model, code=HTTPStatus.CREATED, description="User registered successfully")
    @auth_ns.doc(description="Register a new user")
    def post(self):
        return AuthController.register()


@auth_ns.route('/login')
class Login(Resource):

    @auth_ns.expect(models.login)
    @auth_ns.doc(description="User login")
    def post(self):
        return AuthController.login()


@auth_ns.route('/users')
class UserList(Resource):

    @auth_ns.marshal_with(models.response_list_model)
    @auth_ns.doc(description="List all users (Admin only)")
    @role_required(UserRole.ADMIN)
    def get(self):
        return AuthController.get_all_users()


@auth_ns.route('/logout')
class Logout(Resource):

    @auth_ns.doc(description="User logout (revokes current token)")
    @jwt_required()
    def post(self):
        return AuthController.logout()


@auth_ns.route('/refresh')
class Refresh(Resource):

    @auth_ns.doc(description="Refresh access token using refresh token")
    @jwt_required(refresh=True)
    def post(self):
        return AuthController.refresh()
