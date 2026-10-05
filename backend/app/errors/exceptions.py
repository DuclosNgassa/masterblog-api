from werkzeug.exceptions import HTTPException


class APIError(HTTPException):
    """Base class for custom API exceptions."""

    def __init__(self, message, status_code=400, details=None):
        super().__init__()
        self.code = status_code
        self.description = message
        self.details = details