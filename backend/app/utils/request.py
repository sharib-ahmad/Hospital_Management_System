from flask import request
from .response import handle_response

def validate_json():
    """
    Validates if the request is JSON and contains data.
    Returns (data, error_response) tuple.
    If valid, error_response is None.
    If invalid, data is None and error_response is the Flask response.
    """
    if not request.is_json:
        return None, handle_response(
            success=False, 
            message="Content-Type must be application/json", 
            status_code=400
        )

    data = request.get_json(silent=True)
    if data is None: # Covers cases where get_json fails even if is_json is true
        return None, handle_response(
            success=False, 
            message="Invalid JSON body", 
            status_code=400
        )
        
    return data, None
