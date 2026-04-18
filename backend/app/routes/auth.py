# app/routes/auth.py

from flask import request
from http import HTTPStatus
from flask_restx import Namespace, Resource
from ..api_models import AuthModels
from ..controllers.auth_controller import register_controller, login_controller

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