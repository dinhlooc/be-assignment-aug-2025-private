import uuid
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.postgresql import UUID

class GUID(TypeDecorator):
    """Xử lý UUID giữa các hệ quản trị cơ sở dữ liệu khác nhau."""
    impl = TEXT
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif not isinstance(value, uuid.UUID):
            try:
                return uuid.UUID(value)
            except (TypeError, ValueError):
                return value
        return value