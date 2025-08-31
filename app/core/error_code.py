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
    PROJECT_NOT_FOUND = (2002, "Project not found")
    USER_NOT_IN_ORGANIZATION = (2010, "User is not in the same organization")
    USER_ALREADY_IN_PROJECT = (2011, "User is already a member of this project")
    USER_NOT_IN_PROJECT = (2012, "User is not a member of this project")
    FOREIGN_KEY_VIOLATION = (3001, "Foreign key violation")
    UNIQUE_CONSTRAINT_VIOLATION = (3002, "Unique constraint violation")
    INTEGRITY_ERROR = (3999, "Database integrity error")
    # ... các mã khác
    # Task related error codes
    TASK_NOT_FOUND = (3001, "Task not found")
    TASK_ACCESS_DENIED = (3002, "Task access denied")
    TASK_INVALID_STATUS_TRANSITION = (3003, "Invalid task status transition")
    TASK_ASSIGNEE_NOT_IN_PROJECT = (3004, "Task assignee not in project")
    TASK_ALREADY_ASSIGNED = (3005, "Task already assigned")
    TASK_INVALID_DUE_DATE = (3006, "Invalid task due date")
    TASK_CREATION_FAILED = (3007, "Task creation failed")
    TASK_UPDATE_FAILED = (3008, "Task update failed")
    TASK_DELETE_FAILED = (3009, "Task deletion failed")
    TASK_ASSIGNMENT_FAILED = (3010, "Task assignment failed")
    COMMENT_NOT_FOUND = (4001, "Comment not found")
    COMMENT_ACCESS_DENIED = (4002, "Comment access denied")
    COMMENT_CREATION_FAILED = (4003, "Comment creation failed")
    COMMENT_UPDATE_FAILED = (4004, "Comment update failed")
    COMMENT_DELETE_FAILED = (4005, "Comment delete failed")
    # Thêm vào class ErrorCode
    ATTACHMENT_NOT_FOUND = (5001, "Attachment not found")
    ATTACHMENT_UPLOAD_FAILED = (5002, "Attachment upload failed")
    ATTACHMENT_DELETE_FAILED = (5003, "Attachment delete failed")
    ATTACHMENT_LIMIT_EXCEEDED = (5004, "Attachment limit exceeded")
    ATTACHMENT_FILE_TOO_LARGE = (5005, "Attachment file too large")
    ATTACHMENT_FILE_TYPE_INVALID = (5006, "Attachment file type invalid")
    # Thêm vào class ErrorCode
    NOTIFICATION_NOT_FOUND = (6001, "Notification not found")
    NOTIFICATION_MARK_READ_FAILED = (6002, "Failed to mark notification as read")
    NOTIFICATION_DELETE_FAILED = (6003, "Failed to delete notification")
    NOTIFICATION_CREATE_FAILED = (6004, "Failed to create notification")

    @staticmethod
    def get_code(error):
        return error[0]

    @staticmethod
    def get_message(error):
        return error[1]