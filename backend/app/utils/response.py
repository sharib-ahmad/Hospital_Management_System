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