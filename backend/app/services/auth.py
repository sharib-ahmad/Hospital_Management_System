# app/services/auth.py
from ..models import User, TokenBlocklist
from ..extensions import db
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, current_user
from ..utils.response import success_response, error_response
from ..utils.enum import UserRole
class AuthService:

    @staticmethod
    def register_user(user_data):

        user = User(
            username=user_data.username,
            full_name=user_data.full_name,
            email=user_data.email,
            address=user_data.address,
            phone_number=user_data.phone_number,
            password = user_data.password,
            pincode=user_data.pincode
        )

        try:
            db.session.add(user)
            db.session.commit()
            
            # Send welcome email asynchronously
            from ..tasks.email_tasks import send_welcome_email
            send_welcome_email.delay(user.id)
            
        except IntegrityError:
            db.session.rollback()
            return error_response(message="Username, email or phone number already exists")

        return success_response(
            data=user,
            message="User registered successfully", 
            status=201)


    @staticmethod
    def login_user(login_data):
        user = User.query.filter_by(username=login_data.username).first()

        if user and user.check_password(login_data.password):
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            return success_response(
                data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value
                    }
                },
                message="Login successful"
            )

        return error_response(message="Invalid username or password", status=401)

    @staticmethod
    def logout_user():
        token = get_jwt()
        jti = token["jti"]
        ttype = token["type"]
        user_id = token["sub"]

        new_blocked_token = TokenBlocklist(
            jti=jti,
            type=ttype,
            user_id=user_id
        )

        db.session.add(new_blocked_token)
        db.session.commit()

        return success_response(message="Successfully logged out")

    @staticmethod
    def get_all_users():
        users = User.query.all()
        return success_response(data=users, message="Users retrieved successfully")

    @staticmethod
    def refresh_token():
        # current_user is available if we use @jwt_required(refresh=True)
        # and user_lookup_loader is configured in security.py
        access_token = create_access_token(identity=current_user)
        return success_response(
            data={"access_token": access_token},
            message="Token refreshed successfully"
        )

    @staticmethod
    def reset_password(reset_data):
        user = User.query.filter_by(username=reset_data.username, email=reset_data.email).first()
        if not user:
            return error_response(message="Invalid credentials: username and email do not match", status=404)
        
        user.password = reset_data.new_password
        db.session.commit()
        return success_response(message="Password reset successfully")
