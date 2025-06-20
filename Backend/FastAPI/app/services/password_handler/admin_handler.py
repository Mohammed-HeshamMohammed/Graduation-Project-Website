# app/services/password_handler/admin_handler.py
"""
Administrative functions for password management
"""

from fastapi import Request
from typing import Dict, Any, Optional
import logging

from app.services.storage import UserStorage
from .validators import get_audit_context
from .history_manager import _password_history_service
from .exceptions import UserNotFoundError, PasswordHistoryError

logger = logging.getLogger(__name__)

class PasswordAdminHandler:
    """Handler for administrative password management functions"""
    
    def __init__(self):
        self.user_storage = UserStorage()
        self.password_history_manager = _password_history_service.password_history_manager

# Create singleton instance
_admin_handler = PasswordAdminHandler()

async def get_user_password_history_stats(
    user_email: str,
    request: Request = None
) -> Dict[str, Any]:
    """
    Get password history statistics for a user (admin function)
    """
    try:
        if not _admin_handler.password_history_manager:
            return {"error": "Password history system not available"}
        
        user = _admin_handler.user_storage.get_user_by_email(user_email)
        if not user:
            return {"error": "User not found"}
        
        user_uuid = user.get("uuid", user.get("id", user["email"]))
        audit_context = get_audit_context(request, user_email)
        
        # Get password count
        history_count = _admin_handler.password_history_manager.get_password_history_count(
            user_uuid=str(user_uuid),
            **audit_context
        )
        
        return {
            "user_email": user_email,
            "password_history_count": history_count,
            "last_password_change": user.get("password_changed_at"),
        }
        
    except Exception as e:
        logger.error(f"Error getting password history stats for {user_email}: {e}")
        return {"error": "Failed to retrieve password history statistics"}

async def admin_clear_user_password_history(
    target_user_email: str,
    admin_user_email: str,
    request: Request = None
) -> Dict[str, Any]:
    """
    Clear password history for a user (admin only)
    """
    try:
        if not _admin_handler.password_history_manager:
            return {"error": "Password history system not available"}
        
        # Get target user
        target_user = _admin_handler.user_storage.get_user_by_email(target_user_email)
        if not target_user:
            return {"error": "Target user not found"}
        
        # Get admin user
        admin_user = _admin_handler.user_storage.get_user_by_email(admin_user_email)
        if not admin_user or not admin_user.get("is_admin", False):
            return {"error": "Admin access required"}
        
        user_uuid = target_user.get("uuid", target_user.get("id", target_user["email"]))
        company_uuid = target_user.get("company_uuid", target_user.get("company_id", "default_company"))
        admin_uuid = admin_user.get("uuid", admin_user.get("id", admin_user["email"]))
        
        audit_context = get_audit_context(request, admin_user_email)
        
        # Clear user history
        success = _admin_handler.password_history_manager.clear_user_history(
            user_uuid=str(user_uuid),
            company_uuid=str(company_uuid),
            requesting_admin_uuid=str(admin_uuid),
            **audit_context
        )
        
        if success:
            return {"message": f"Password history cleared for user {target_user_email}"}
        else:
            return {"error": "Failed to clear password history"}
            
    except Exception as e:
        logger.error(f"Error clearing password history for {target_user_email}: {e}")
        return {"error": "Failed to clear password history"}

async def get_password_security_summary(
    company_uuid: Optional[str] = None,
    admin_user_email: str = None,
    days: int = 30,
    request: Request = None
) -> Dict[str, Any]:
    """
    Get password security summary (admin function)
    """
    try:
        if not _admin_handler.password_history_manager:
            return {"error": "Password history system not available"}
        
        if admin_user_email:
            admin_user = _admin_handler.user_storage.get_user_by_email(admin_user_email)
            if not admin_user or not admin_user.get("is_admin", False):
                return {"error": "Admin access required"}
            
            admin_uuid = admin_user.get("uuid", admin_user.get("id", admin_user["email"]))
        else:
            admin_uuid = None
        
        # Get security summary
        summary = _admin_handler.password_history_manager.get_security_summary(
            company_uuid=company_uuid,
            days=days,
            requesting_admin_uuid=str(admin_uuid) if admin_uuid else None
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting security summary: {e}")
        return {"error": "Failed to retrieve security summary"}

async def bulk_password_policy_update(
    company_uuid: str,
    new_policy: Dict[str, Any],
    admin_user_email: str,
    request: Request = None
) -> Dict[str, Any]:
    """
    Update password policy for a company (admin function)
    """
    try:
        if not _admin_handler.password_history_manager:
            return {"error": "Password history system not available"}
        
        # Verify admin access
        admin_user = _admin_handler.user_storage.get_user_by_email(admin_user_email)
        if not admin_user or not admin_user.get("is_admin", False):
            return {"error": "Admin access required"}
        
        admin_uuid = admin_user.get("uuid", admin_user.get("id", admin_user["email"]))
        audit_context = get_audit_context(request, admin_user_email)
        
        # Validate policy structure
        required_fields = ["max_history", "min_password_age", "max_password_age"]
        if not all(field in new_policy for field in required_fields):
            return {"error": f"Policy must include: {', '.join(required_fields)}"}
        
        # Update policy (this would be implemented in the enterprise system)
        # For now, return success message
        logger.info(f"Password policy update requested by {admin_user_email} for company {company_uuid}")
        
        return {
            "message": "Password policy update initiated",
            "company_uuid": company_uuid,
            "updated_by": admin_user_email,
            "policy": new_policy
        }
        
    except Exception as e:
        logger.error(f"Error updating password policy: {e}")
        return {"error": "Failed to update password policy"}

async def get_company_password_metrics(
    company_uuid: str,
    admin_user_email: str,
    request: Request = None
) -> Dict[str, Any]:
    """
    Get password security metrics for a company (admin function)
    """
    try:
        if not _admin_handler.password_history_manager:
            return {"error": "Password history system not available"}
        
        # Verify admin access
        admin_user = _admin_handler.user_storage.get_user_by_email(admin_user_email)
        if not admin_user or not admin_user.get("is_admin", False):
            return {"error": "Admin access required"}
        
        # Get all users for the company
        # This would typically be a method in UserStorage
        # For now, we'll simulate the metrics
        
        metrics = {
            "company_uuid": company_uuid,
            "total_users": 0,
            "users_with_recent_password_changes": 0,
            "average_password_age_days": 0,
            "password_policy_violations": 0,
            "password_reuse_attempts_blocked": 0
        }
        
        # In a real implementation, you would query the database and 
        # password history system to get actual metrics
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting company password metrics: {e}")
        return {"error": "Failed to retrieve password metrics"}