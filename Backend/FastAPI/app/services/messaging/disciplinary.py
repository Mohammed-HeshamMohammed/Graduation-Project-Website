"""
Disciplinary Action Manager Module

Handles warning and disciplinary action messaging functionality.
"""

import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from .access_control import MessageAccessControl

logger = logging.getLogger(__name__)


class DisciplinaryActionManager:
    """Manages warning and disciplinary action messages"""
    
    def __init__(self, user_storage, add_message_callback):
        """Initialize disciplinary action manager
        
        Args:
            user_storage: UserStorage instance
            add_message_callback: Callback function to add messages
        """
        self.user_storage = user_storage
        self.add_message = add_message_callback
        self.access_control = MessageAccessControl()
    
    def send_warning_to_subordinates(self, sender_uuid: str, message: str, 
                                   target_user_uuids: List[str] = None) -> Dict[str, Any]:
        """
        Send warning messages to users under the sender in the privilege hierarchy.
        Only managers, admins, and owners can use this function.
        
        Args:
            sender_uuid: UUID of the user sending the warning
            message: Warning message content
            target_user_uuids: Optional list of specific user UUIDs to target. 
                              If None, sends to all subordinates.
        
        Returns:
            dict: Results including success count and details
        """
        try:
            # Get sender information
            sender_user = self.user_storage.get_user_by_uuid(sender_uuid)
            if not sender_user:
                logger.error(f"Sender user not found: {sender_uuid}")
                return {"success": False, "error": "Sender not found"}
            
            sender_privileges = sender_user.get('privileges', [])
            sender_company_id = sender_user.get('company_id')
            
            # Check if sender has authority to send warnings
            if not self.access_control.can_send_warnings(sender_privileges):
                logger.warning(f"User {sender_uuid} lacks authority to send warnings")
                return {"success": False, "error": "Insufficient privileges to send warnings"}
            
            # Find subordinate users
            subordinate_users = self._find_subordinates(
                sender_uuid, sender_company_id, sender_privileges, target_user_uuids
            )
            
            if not subordinate_users:
                return {
                    "success": True, 
                    "message": "No subordinates found to send warnings to",
                    "sent_count": 0,
                    "targets": []
                }
            
            # Send warning messages
            success_count = 0
            failed_users = []
            successful_users = []
            
            # Create enhanced warning message with sender info
            warning_content = self._create_warning_message(sender_user, message)
            
            for user in subordinate_users:
                if self.add_message(user['uuid'], warning_content, sender_uuid, "warning"):
                    success_count += 1
                    successful_users.append({
                        'uuid': user['uuid'],
                        'email': user['email'],
                        'full_name': user['full_name']
                    })
                else:
                    failed_users.append({
                        'uuid': user['uuid'],
                        'email': user['email'],
                        'full_name': user['full_name']
                    })
            
            # Log the warning action
            logger.info(f"Warning sent by {sender_user.get('email')} to {success_count}/{len(subordinate_users)} subordinates")
            
            return {
                "success": success_count > 0,
                "sent_count": success_count,
                "total_targets": len(subordinate_users),
                "successful_users": successful_users,
                "failed_users": failed_users,
                "sender_info": {
                    "email": sender_user.get('email'),
                    "full_name": sender_user.get('full_name'),
                    "privileges": sender_privileges
                }
            }
            
        except Exception as e:
            logger.error(f"Error sending warning to subordinates: {type(e).__name__}: {e}")
            return {"success": False, "error": f"System error: {str(e)}"}
    
    def send_disciplinary_action(self, sender_uuid: str, target_user_uuid: str, 
                               action_type: str, message: str, severity: str = "medium") -> Dict[str, Any]:
        """
        Send disciplinary action messages to specific users.
        Only admins and owners can use this function.
        
        Args:
            sender_uuid: UUID of the user sending the disciplinary action
            target_user_uuid: UUID of the user receiving the action
            action_type: Type of action (warning, suspension, review, etc.)
            message: Detailed message about the action
            severity: Severity level (low, medium, high, critical)
        
        Returns:
            dict: Results of the disciplinary action
        """
        try:
            # Get sender information
            sender_user = self.user_storage.get_user_by_uuid(sender_uuid)
            if not sender_user:
                logger.error(f"Sender user not found: {sender_uuid}")
                return {"success": False, "error": "Sender not found"}
            
            sender_privileges = sender_user.get('privileges', [])
            sender_company_id = sender_user.get('company_id')
            
            # Check if sender has authority
            if not self.access_control.can_send_disciplinary_actions(sender_privileges):
                logger.warning(f"User {sender_uuid} lacks authority to send disciplinary actions")
                return {"success": False, "error": "Only owners and admins can send disciplinary actions"}
            
            # Get target user information
            target_user = self.user_storage.get_user_by_uuid(target_user_uuid)
            if not target_user:
                logger.error(f"Target user not found: {target_user_uuid}")
                return {"success": False, "error": "Target user not found"}
            
            target_company_id = target_user.get('company_id')
            target_privileges = target_user.get('privileges', [])
            
            # Must be same company
            if sender_company_id != target_company_id:
                logger.warning(f"Cross-company disciplinary action attempted: {sender_uuid} -> {target_user_uuid}")
                return {"success": False, "error": "Cannot send disciplinary actions to users from different companies"}
            
            # Check if sender can discipline target
            if not self.access_control.can_discipline_user(sender_privileges, target_privileges):
                logger.warning(f"Admin attempted to discipline owner: {sender_uuid} -> {target_user_uuid}")
                return {"success": False, "error": "Admins cannot send disciplinary actions to owners"}
            
            # Create and send disciplinary message
            disciplinary_content = self._create_disciplinary_message(
                sender_user, action_type, message, severity
            )
            
            success = self.add_message(target_user_uuid, disciplinary_content, sender_uuid, "disciplinary")
            
            if success:
                logger.info(f"Disciplinary action '{action_type}' sent by {sender_user.get('email')} to {target_user.get('email')}")
                
                return {
                    "success": True,
                    "action_type": action_type,
                    "severity": severity,
                    "target_user": {
                        "uuid": target_user_uuid,
                        "email": target_user.get('email'),
                        "full_name": target_user.get('full_name')
                    },
                    "sender_info": {
                        "email": sender_user.get('email'),
                        "full_name": sender_user.get('full_name')
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to send disciplinary message"}
            
        except Exception as e:
            logger.error(f"Error sending disciplinary action: {type(e).__name__}: {e}")
            return {"success": False, "error": f"System error: {str(e)}"}
    
    def _find_subordinates(self, sender_uuid: str, sender_company_id: str, 
                          sender_privileges: List[str], target_user_uuids: Optional[List[str]]) -> List[Dict[str, Any]]:
        """Find all subordinate users for the sender"""
        subordinate_users = []
        
        for email, user_data in self.user_storage.users.items():
            if not isinstance(user_data, dict):
                continue
            
            user_uuid = user_data.get('uuid')
            user_company_id = user_data.get('company_id')
            user_privileges = user_data.get('privileges', [])
            
            # Skip if not in same company
            if user_company_id != sender_company_id:
                continue
            
            # Skip self
            if user_uuid == sender_uuid:
                continue
            
            # If specific targets provided, only include those
            if target_user_uuids and user_uuid not in target_user_uuids:
                continue
            
            # Check if user is subordinate
            if self.access_control.is_subordinate(sender_privileges, user_privileges):
                subordinate_users.append({
                    'uuid': user_uuid,
                    'email': email,
                    'full_name': user_data.get('full_name', ''),
                    'privileges': user_privileges
                })
        
        return subordinate_users
    
    def _create_warning_message(self, sender_user: Dict[str, Any], message: str) -> str:
        """Create formatted warning message"""
        return (f"⚠️ WARNING FROM {sender_user.get('full_name', 'Management')}\n\n"
                f"{message}\n\n"
                f"--- \n"
                f"Sent by: {sender_user.get('full_name')} ({sender_user.get('email')})\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _create_disciplinary_message(self, sender_user: Dict[str, Any], action_type: str, 
                                   message: str, severity: str) -> str:
        """Create formatted disciplinary action message"""
        severity_icons = {
            "low": "ℹ️",
            "medium": "⚠️", 
            "high": "🚨",
            "critical": "🔥"
        }
        
        icon = severity_icons.get(severity.lower(), "⚠️")
        
        return (f"{icon} DISCIPLINARY ACTION - {action_type.upper()}\n"
                f"Severity: {severity.upper()}\n\n"
                f"{message}\n\n"
                f"---\n"
                f"Issued by: {sender_user.get('full_name')} ({sender_user.get('email')})\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Action ID: DA_{int(time.time())}")