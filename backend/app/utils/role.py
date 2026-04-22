from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request, jwt_required
from .response import handle_response
from .enum import UserRole

def role_required(*required_roles):
    """
    Decorator to restrict access to one or more specific roles.
    Usage: @role_required(UserRole.ADMIN) or @role_required(UserRole.ADMIN, UserRole.DOCTOR)
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            # Ensure JWT is valid and present
            verify_jwt_in_request()
            
            claims = get_jwt()
            user_role = claims.get("role")
            
            # Resolve the required role values
            allowed_roles = []
            for role in required_roles:
                if isinstance(role, UserRole):
                    allowed_roles.append(role.value)
                else:
                    allowed_roles.append(str(role))
            
            if user_role in allowed_roles:
                return fn(*args, **kwargs)
            
            allowed_roles_str = ", ".join(allowed_roles)
            return handle_response(
                message=f"Access denied. This route is restricted to {allowed_roles_str} only.",
                status_code=403
            )
        return wrapper
    return decorator
