def success_response(data=None, message="Success", status=200):
    return {
        "success": True,
        "message": message,
        "data": data
    }, status


def error_response(message="Error", errors=None, status=400):
    return {
        "success": False,
        "message": message,
        "errors": errors
    }, status
    
def handle_response(success=True, message="", data=None, errors=None, status_code=200):
    if success:
        return success_response(data=data, message=message, status=status_code)
    else:
        return error_response(message=message, errors=errors, status=status_code)