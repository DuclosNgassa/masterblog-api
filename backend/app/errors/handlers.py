
from flask import Blueprint, jsonify
from werkzeug.exceptions import HTTPException
from app.errors.exceptions import APIError

errors_bp = Blueprint('errors', __name__)


# Handles custom API exceptions globally
@errors_bp.app_errorhandler(APIError)
def handle_api_error(error):
    response = {
        'error': error.name,
        'message': error.description,
        'status': error.code,
    }
    if error.details:
        response['details'] = error.details
    return jsonify(response), error.code


# Catch-all for built-in HTTP exceptions (404, 405, 500, etc.)
@errors_bp.app_errorhandler(HTTPException)
def handle_http_exception(e):
    return (
        jsonify({
            'error': e.name,
            'message': e.description,
            'status': e.code,
        }),
        e.code,
    )