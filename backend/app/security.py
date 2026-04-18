import uuid
from app.models.user import User
from app.extensions import jwt


@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(uuid.UUID(identity))

# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     token = TokenBlocklist.query.filter_by(jti=jti).first()
#     return token is not None