from fastapi.responses import JSONResponse
from app.schemas.response.api_response import APIResponse
from app.core.error_code import ErrorCode
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import DomainException
from fastapi import Request
from sqlalchemy.exc import IntegrityError


async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_response().model_dump()
    )

async def global_exception_handler(request, exc):
    if isinstance(exc, IntegrityError):
        # Kiểm tra lỗi khóa ngoại
        if "violates foreign key constraint" in str(exc.orig):
            message = "Organization does not exist"
            code = ErrorCode.get_code(ErrorCode.FOREIGN_KEY_VIOLATION)
        else:
            message = "Database integrity error"
            code = ErrorCode.get_code(ErrorCode.INTEGRITY_ERROR)
        return JSONResponse(
            status_code=400,
            content=APIResponse(
                code=code,
                message=message,
                result=str(exc.orig)
            ).model_dump()
        )
    return JSONResponse(
        status_code=400,
        content=APIResponse(
            code=ErrorCode.get_code(ErrorCode.UNCATEGORIZED_EXCEPTION),
            message=ErrorCode.get_message(ErrorCode.UNCATEGORIZED_EXCEPTION),
            result=None
        ).model_dump()
    )

async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            code=ErrorCode.get_code(ErrorCode.VALIDATION_ERROR),
            message=ErrorCode.get_message(ErrorCode.VALIDATION_ERROR),
            result=exc.errors()
        ).model_dump()
    )