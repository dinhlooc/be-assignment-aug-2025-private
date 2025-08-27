class ErrorCode:
    SUCCESS = (200, "Success")
    VALIDATION_ERROR = (1001, "Validation Error")
    UNCATEGORIZED_EXCEPTION = (1999, "Uncategorized Exception")
    EMAIL_ALREADY_EXISTS = (1002, "Email already registered")
    INVALID_CREDENTIALS = (1003, "Invalid credentials")
    ORGANIZATION_NAME_EXISTS = (1004, "Organization name already exists")
    ORGANIZATION_NOT_FOUND = (1005, "Organization not found")
    USER_NOT_FOUND = (1006, "User not found")
    NOT_FOUND = (1009, "Resource not found")
    AUTH_FAILED = (1007, "Authentication failed")
    AUTHZ_FAILED = (1008, "Not authorized")
    UNCATEGORIZED_EXCEPTION = (1999, "Uncategorized Exception")
    PROJECT_NAME_EXISTS = (2001, "Project with this name already exists in your organization")
    USER_NOT_IN_ORGANIZATION = (2010, "User is not in the same organization")
    USER_ALREADY_IN_PROJECT = (2011, "User is already a member of this project")
    USER_NOT_IN_PROJECT = (2012, "User is not a member of this project")
    FOREIGN_KEY_VIOLATION = (3001, "Foreign key violation")
    UNIQUE_CONSTRAINT_VIOLATION = (3002, "Unique constraint violation")
    INTEGRITY_ERROR = (3999, "Database integrity error")
    # ... các mã khác

    @staticmethod
    def get_code(error):
        return error[0]

    @staticmethod
    def get_message(error):
        return error[1]