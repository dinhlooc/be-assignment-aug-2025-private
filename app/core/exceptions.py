from fastapi import HTTPException, status
from app.core.error_code import ErrorCode
from app.schemas.response.api_response import APIResponse

class DomainException(Exception):
    code: int = ErrorCode.UNCATEGORIZED_EXCEPTION[0]
    message: str = ErrorCode.UNCATEGORIZED_EXCEPTION[1]
    http_status: int = 400

    def to_response(self):
        return APIResponse(
            code=self.code,
            message=self.message,
            result=None
        )
    
class EmailAlreadyExistsException(DomainException):
    code = ErrorCode.EMAIL_ALREADY_EXISTS[0]
    message = ErrorCode.EMAIL_ALREADY_EXISTS[1]
    http_status = 400

class OrganizationNameExistsException(DomainException):
    code = ErrorCode.ORGANIZATION_NAME_EXISTS[0]
    message = ErrorCode.ORGANIZATION_NAME_EXISTS[1]
    http_status = 400

class InvalidCredentialsException(DomainException):
    code = ErrorCode.INVALID_CREDENTIALS[0]
    message = ErrorCode.INVALID_CREDENTIALS[1]
    http_status = 401

class AuthenticationFailedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.AUTH_FAILED)
    message = ErrorCode.get_message(ErrorCode.AUTH_FAILED)
    http_status = 401

class AuthorizationFailedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.AUTHZ_FAILED)
    def __init__(self, message=None):
        # Nếu truyền message thì dùng, không thì dùng default
        if message is None:
            message = ErrorCode.get_message(ErrorCode.AUTHZ_FAILED)
        self.message = message
        super().__init__(self.message)
    http_status = 403

class UserNotFoundException(DomainException):
    code = ErrorCode.get_code(ErrorCode.USER_NOT_FOUND)
    message = ErrorCode.get_message(ErrorCode.USER_NOT_FOUND)
    http_status = 404

class NotFoundException(DomainException):
    code = ErrorCode.get_code(ErrorCode.NOT_FOUND)
    message = ErrorCode.get_message(ErrorCode.NOT_FOUND)
    http_status = 404

class ForeignKeyViolationException(DomainException):
    def __init__(self, result=None):
        super().__init__(ErrorCode.FOREIGN_KEY_VIOLATION, http_status=409, result=result)

class UniqueConstraintViolationException(DomainException):
    def __init__(self, result=None):
        super().__init__(ErrorCode.UNIQUE_CONSTRAINT_VIOLATION, http_status=409, result=result)

class IntegrityErrorException(DomainException):
    def __init__(self, result=None):
        super().__init__(ErrorCode.INTEGRITY_ERROR, http_status=409, result=result)
