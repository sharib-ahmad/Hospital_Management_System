# app/routes/auth.py

from flask import request
from http import HTTPStatus
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required
from ..api_models import AuthModels
from ..controllers.auth_controller import register_controller, login_controller, logout_controller, refresh_controller

auth_ns = Namespace('auth', description='Authentication related operations')

models = AuthModels(auth_ns)


@auth_ns.route('/register')
class Register(Resource):

    @auth_ns.expect(models.register)
    @auth_ns.marshal_with(models.response_model, code=HTTPStatus.CREATED, description="User registered successfully")
    @auth_ns.doc(description="Register a new user")
    def post(self):
        return register_controller(request)


@auth_ns.route('/login')
class Login(Resource):

    @auth_ns.expect(models.login)
    @auth_ns.doc(description="User login")
    def post(self):
        return login_controller(request)


@auth_ns.route('/logout')
class Logout(Resource):

    @auth_ns.doc(description="User logout (revokes current token)")
    @jwt_required()
    def post(self):
        return logout_controller()


@auth_ns.route('/refresh')
class Refresh(Resource):

    @auth_ns.doc(description="Refresh access token using refresh token")
    @jwt_required(refresh=True)
    def post(self):
        return refresh_controller()
