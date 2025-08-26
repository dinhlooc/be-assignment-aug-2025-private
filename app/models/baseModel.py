from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class BaseModel(Base):
    __abstract__ = True  
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())