from app.core.errors import ConflictError, ErrorCode, ForbiddenError, NotFoundError


class UserNotFoundError(NotFoundError):
    error_code = ErrorCode.USER_NOT_FOUND
    default_detail = "User not found"


class EmailTakenError(ConflictError):
    error_code = ErrorCode.EMAIL_TAKEN
    default_detail = "This email is already registered"


class AccountBannedError(ForbiddenError):
    error_code = ErrorCode.ACCOUNT_BANNED
    default_detail = "Your account is banned"


class SelfModerationError(ForbiddenError):
    error_code = ErrorCode.SELF_MODERATION
    default_detail = "You can't ban yourself or change your own role"


class AdminProtectedError(ForbiddenError):
    error_code = ErrorCode.ADMIN_PROTECTED
    default_detail = "Administrators can't be banned; demote them first"
