from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from .response import error_response
from ..models import UserRole

def role_required(required_role):
    """
    Decorator to restrict access to a single specific role.
    Usage: @role_required(UserRole.ADMIN)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure JWT is valid and present
            verify_jwt_in_request()
            
            claims = get_jwt()
            user_role = claims.get("role")
            
            # Resolve the required role value
            if isinstance(required_role, UserRole):
                target_role = required_role.value
            else:
                target_role = str(required_role)
            
            if user_role == target_role:
                return fn(*args, **kwargs)
            
            return error_response(
                message=f"Access denied. This route is restricted to {target_role} only.",
                status=403
            )
        return wrapper
    return decorator
