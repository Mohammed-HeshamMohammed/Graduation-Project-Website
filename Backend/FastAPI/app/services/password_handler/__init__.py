"""
Password handler package for user password operations.
"""

from .validators import (
    validate_token,
    validate_password_strength,
    validate_password_match,
    get_audit_context,
)
from .exceptions import (
    PasswordHandlerException,
    PasswordValidationError,
    PasswordHistoryError,
    TokenValidationError,
    UserNotFoundError,
    RateLimitExceededError,
)
from .history_manager import (
    check_password_with_history,
    update_user_password_with_history,
)
from .reset_handler import (
    forgot_password,
    reset_password_form,
    reset_password_confirm,
)
from .change_handler import (
    change_password,
)
from .admin_handler import (
    get_user_password_history_stats,
    admin_clear_user_password_history,
    get_password_security_summary,
    bulk_password_policy_update,
    get_company_password_metrics,
)

__version__ = "1.0.0"

__all__ = [
    # validators
    "validate_token",
    "validate_password_strength",
    "validate_password_match",
    "get_audit_context",
    # exceptions
    "PasswordHandlerException",
    "PasswordValidationError",
    "PasswordHistoryError",
    "TokenValidationError",
    "UserNotFoundError",
    "RateLimitExceededError",
    # history manager
    "check_password_with_history",
    "update_user_password_with_history",
    # reset handler
    "forgot_password",
    "reset_password_form",
    "reset_password_confirm",
    # change handler
    "change_password",
    # admin handler
    "get_user_password_history_stats",
    "admin_clear_user_password_history",
    "get_password_security_summary",
    "bulk_password_policy_update",
    "get_company_password_metrics",
]