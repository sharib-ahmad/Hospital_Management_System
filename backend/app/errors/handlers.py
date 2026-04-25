from .exceptions import AppError
from ..utils.response import handle_response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

def register_error_handlers(api):
    @api.errorhandler(AppError)
    def handle_app_error(error):
        return handle_response(
            success=False,
            message=error.message,
            status_code=error.status_code
        )

    @api.errorhandler(ValidationError)
    def handle_pydantic_validation_error(error):
        return handle_response(
            success=False,
            message="Validation Error",
            errors=error.errors(),
            status_code=400
        )

    @api.errorhandler(HTTPException)
    def handle_http_exception(error):
        return handle_response(
            success=False,
            message=error.description,
            status_code=error.code
        )

    @api.errorhandler(Exception)
    def handle_general_exception(error):
        # In production, you might want to log this and return a generic message
        return handle_response(
            success=False,
            message=str(error),
            status_code=500
        )
