from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_restx import Api

db = SQLAlchemy()
jwt = JWTManager()

api = Api(version='1.0',
        title='Hospital Management System API',
        description='API for hospital management system',
        authorizations={
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': "Add a JWT token like this: Bearer <your_token_here>"
            }
        },
        security='Bearer Auth',
        doc='/docs')  