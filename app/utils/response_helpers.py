from flask import jsonify
from app.models.data_models import ErrorResponse


def create_error_response(
    error_code: str,
    message: str,
    details: str = None,
    status_code: int = 400,
    retry_after: int = None,
):
    """Helper to create standardized error responses"""
    error = ErrorResponse.create(error_code, message, details, retry_after)
    response = jsonify(error.model_dump())
    response.status_code = status_code
    if retry_after:
        response.headers["Retry-After"] = str(retry_after)
    return response
