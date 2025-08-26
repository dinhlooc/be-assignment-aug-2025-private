from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(organizations.router, prefix="/api/v1", tags=["Organizations"])
app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
app.include_router(comments.router, prefix="/api/v1", tags=["Comments"])
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
