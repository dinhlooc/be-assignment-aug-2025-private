from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.core.middleware import LoggingMiddleware
from app.core.handdlers import global_exception_handler,validation_exception_handler, domain_exception_handler
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import DomainException
from sqlalchemy.exc import IntegrityError

from app.routers import (
    auth,
    users,
    organizations,
    projects,
    tasks,
    comments,
    attachments,
    notifications,
    reports,
)

app = FastAPI(
    title="Task Management API",
    description="Multi-organization Task Management Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Nếu components chưa tồn tại, khởi tạo
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    # Thêm securitySchemes mà không ghi đè các components khác
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Nhập JWT Token của bạn với tiền tố 'Bearer '"
        }
    }

    # Áp dụng security requirement cho tất cả các endpoints
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    for path in openapi_schema["paths"]:
        if path == "/api/v1/auth/login":
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = []

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# CORS middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(IntegrityError, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DomainException, domain_exception_handler)
# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(attachments.router, prefix="/api/v1", tags=["Attachments"])
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])


@app.get("/")
async def root():
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
def startup_event():
    try:
        from app.repositories.notification import redis_client
        redis_client.ping()
        print("✅ Redis connected successfully")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")