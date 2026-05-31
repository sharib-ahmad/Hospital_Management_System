from .exceptions import AppError
from ..utils.response import handle_response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jwt.exceptions import PyJWTError
from flask_jwt_extended.exceptions import JWTExtendedException
import logging

logger = logging.getLogger(__name__)

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

    @api.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        logger.error(f"Integrity Error: {str(error)}")
        return handle_response(
            success=False,
            message="A record with this information already exists.",
            status_code=409
        )

    @api.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        logger.error(f"Database Error: {str(error)}")
        return handle_response(
            success=False,
            message="A database error occurred while processing your request. Please try again later.",
            status_code=500
        )

    @api.errorhandler(HTTPException)
    def handle_http_exception(error):
        return handle_response(
            success=False,
            message=error.description,
            status_code=error.code
        )

    @api.errorhandler(PyJWTError)
    def handle_jwt_error(error):
        logger.warning(f"JWT/Token Error: {str(error)}")
        return handle_response(
            success=False,
            message=str(error),
            status_code=401
        )

    @api.errorhandler(JWTExtendedException)
    def handle_jwt_extended_error(error):
        logger.warning(f"Flask-JWT-Extended Error: {str(error)}")
        return handle_response(
            success=False,
            message=str(error),
            status_code=401
        )

    @api.errorhandler(Exception)
    def handle_general_exception(error):
        logger.exception(f"Unhandled Exception: {str(error)}")
        return handle_response(
            success=False,
            message="An unexpected error occurred. Please contact support if the issue persists.",
            status_code=500
        )
