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
        
class ProjectNameExistsException(DomainException):
    code = ErrorCode.get_code(ErrorCode.PROJECT_NAME_EXISTS)
    message = ErrorCode.get_message(ErrorCode.PROJECT_NAME_EXISTS)
    http_status = 400

class ProjectNotFoundException(DomainException):
    code = ErrorCode.get_code(ErrorCode.PROJECT_NOT_FOUND)
    message = ErrorCode.get_message(ErrorCode.PROJECT_NOT_FOUND)
    http_status = 404

class UserNotInOrganizationException(DomainException):
    code = ErrorCode.get_code(ErrorCode.USER_NOT_IN_ORGANIZATION)
    message = ErrorCode.get_message(ErrorCode.USER_NOT_IN_ORGANIZATION)
    http_status = 400

class UserAlreadyInProjectException(DomainException):
    code = ErrorCode.get_code(ErrorCode.USER_ALREADY_IN_PROJECT)
    message = ErrorCode.get_message(ErrorCode.USER_ALREADY_IN_PROJECT)
    http_status = 400

class UserNotInProjectException(DomainException):
    code = ErrorCode.get_code(ErrorCode.USER_NOT_IN_PROJECT)
    message = ErrorCode.get_message(ErrorCode.USER_NOT_IN_PROJECT)
    http_status = 404 

class TaskNotFoundException(DomainException):
    code = ErrorCode.get_code(ErrorCode.TASK_NOT_FOUND)
    message = ErrorCode.get_message(ErrorCode.TASK_NOT_FOUND)
    http_status = 404

class TaskAccessDeniedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.TASK_ACCESS_DENIED)
    def __init__(self, message=None):
        if message is None:
            message = ErrorCode.get_message(ErrorCode.TASK_ACCESS_DENIED)
        self.message = message
        super().__init__(self.message)
    http_status = 403

class TaskInvalidStatusTransitionException(DomainException):
    code = ErrorCode.get_code(ErrorCode.TASK_INVALID_STATUS_TRANSITION)
    message = ErrorCode.get_message(ErrorCode.TASK_INVALID_STATUS_TRANSITION)
    http_status = 400

class TaskAssigneeNotInProjectException(DomainException):
    code = ErrorCode.get_code(ErrorCode.TASK_ASSIGNEE_NOT_IN_PROJECT)
    message = ErrorCode.get_message(ErrorCode.TASK_ASSIGNEE_NOT_IN_PROJECT)
    http_status = 400

class TaskInvalidDueDateException(DomainException):
    code = ErrorCode.get_code(ErrorCode.TASK_INVALID_DUE_DATE)
    message = ErrorCode.get_message(ErrorCode.TASK_INVALID_DUE_DATE)
    http_status = 400

class CommentNotFoundException(DomainException):
    code = ErrorCode.get_code(ErrorCode.COMMENT_NOT_FOUND)
    message = ErrorCode.get_message(ErrorCode.COMMENT_NOT_FOUND)
    http_status = 404

class CommentAccessDeniedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.COMMENT_ACCESS_DENIED)
    
    def __init__(self, message=None):
        if message is None:
            message = ErrorCode.get_message(ErrorCode.COMMENT_ACCESS_DENIED)
        self.message = message
        super().__init__(self.message)
    
    http_status = 403

class CommentCreationFailedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.COMMENT_CREATION_FAILED)
    
    def __init__(self, message=None):
        if message is None:
            message = ErrorCode.get_message(ErrorCode.COMMENT_CREATION_FAILED)
        self.message = message
        super().__init__(self.message)
    
    http_status = 400

class CommentUpdateFailedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.COMMENT_UPDATE_FAILED)
    
    def __init__(self, message=None):
        if message is None:
            message = ErrorCode.get_message(ErrorCode.COMMENT_UPDATE_FAILED)
        self.message = message
        super().__init__(self.message)
    
    http_status = 400

class CommentDeleteFailedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.COMMENT_DELETE_FAILED)
    
    def __init__(self, message=None):
        if message is None:
            message = ErrorCode.get_message(ErrorCode.COMMENT_DELETE_FAILED)
        self.message = message
        super().__init__(self.message)
    
    http_status = 400


class AttachmentNotFoundException(DomainException):
    code = ErrorCode.get_code(ErrorCode.ATTACHMENT_NOT_FOUND)
    message = ErrorCode.get_message(ErrorCode.ATTACHMENT_NOT_FOUND)
    http_status = 404

class AttachmentUploadFailedException(DomainException):
    code = ErrorCode.get_code(ErrorCode.ATTACHMENT_UPLOAD_FAILED)
    message = ErrorCode.get_message(ErrorCode.ATTACHMENT_UPLOAD_FAILED)
    http_status = 400

class AttachmentDeleteFailedException(DomainException):
    def __init__(self, message=None):
        if message is None:
            message = ErrorCode.get_message(ErrorCode.ATTACHMENT_DELETE_FAILED)
        self.message = message
        super().__init__(self.message)

class AttachmentLimitExceededException(DomainException):
    code = ErrorCode.get_code(ErrorCode.ATTACHMENT_LIMIT_EXCEEDED)
    message = ErrorCode.get_message(ErrorCode.ATTACHMENT_LIMIT_EXCEEDED)
    http_status = 400

class AttachmentFileTooLargeException(DomainException):
    code = ErrorCode.get_code(ErrorCode.ATTACHMENT_FILE_TOO_LARGE)
    message = ErrorCode.get_message(ErrorCode.ATTACHMENT_FILE_TOO_LARGE)
    http_status = 400

class AttachmentFileTypeInvalidException(DomainException):
    code = ErrorCode.get_code(ErrorCode.ATTACHMENT_FILE_TYPE_INVALID)
    message = ErrorCode.get_message(ErrorCode.ATTACHMENT_FILE_TYPE_INVALID)
    http_status = 400