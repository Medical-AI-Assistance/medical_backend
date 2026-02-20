# Global Parameters - Constants and Response Messages

# Success Messages
SUCCESS_MESSAGE = "Operation completed successfully"
SUCCESS_CREATED = "Resource created successfully"
SUCCESS_UPDATED = "Resource updated successfully"
SUCCESS_DELETED = "Resource deleted successfully"

# Error Messages
ERROR_INVALID_INPUT = "Invalid input provided"
ERROR_NOT_FOUND = "Resource not found"
ERROR_UNAUTHORIZED = "Unauthorized access"
ERROR_FORBIDDEN = "Access forbidden"
ERROR_SERVER_ERROR = "Internal server error"
ERROR_BAD_REQUEST = "Bad request"

# Validation Messages
VALIDATION_EMAIL_INVALID = "Email is invalid"
VALIDATION_PASSWORD_WEAK = "Password is too weak"
VALIDATION_REQUIRED_FIELD = "This field is required"
VALIDATION_LENGTH_ERROR = "Input length is invalid"
VALIDATION_INVALID_COMBINATION_CREDENTIALS = "Invalid combination of credentials"


# Status Codes
STATUS_SUCCESS = 200
STATUS_CREATED = 201
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_SERVER_ERROR = 500

# Default Values
DEFAULT_PAGE_SIZE = 10
DEFAULT_PAGE_NUMBER = 1
DEFAULT_TIMEOUT = 30

# Response Format
RESPONSE_SUCCESS = {"status": "success", "message": SUCCESS_MESSAGE}
RESPONSE_ERROR = {"status": "error", "message": ERROR_SERVER_ERROR}
MESSAGE = "message"
