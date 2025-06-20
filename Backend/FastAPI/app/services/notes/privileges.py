"""
Privilege management for notes operations.
"""

import logging
from typing import List, Dict, Any
from .exceptions import InsufficientPrivilegesError, CompanyMismatchError

logger = logging.getLogger(__name__)


class NotesPrivilegeManager:
    """Manages privilege-based access control for notes operations."""
    
    def __init__(self):
        self.PRIVILEGE_HIERARCHY = {
            "dashboard_access": [
                "owner", "admin", "manager", "dispatcher",
                "engineer", "fuel_manager", "fleet_officer", "analyst", "viewer"
            ],
            "trip_management": [
                "owner", "admin", "manager", "dispatcher"
            ],
            "maintenance_access": [
                "owner", "admin", "manager", "engineer"
            ],
            "fuel_access": [
                "owner", "admin", "manager", "fuel_manager"  
            ],
            "fleet_management": [
                "owner", "admin", "manager", "fleet_officer"
            ],
            "analytics_access": [
                "owner", "admin", "manager", "analyst"
            ],
            "view_only": [
                "viewer", "analyst"
            ],
            "user_management": [
                "owner", "admin", "add", "remove"
            ],
            "notes_read": [
                "owner", "admin", "manager", "dispatcher",
                "engineer", "fuel_manager", "fleet_officer", "analyst", "viewer"
            ],
            "notes_write": [
                "owner", "admin", "manager"
            ],
            "notes_edit": [
                "owner", "admin", "manager"
            ],
            "notes_delete": [
                "owner", "admin"
            ],
            "notes_export": [
                "owner", "admin"
            ]
        }
    
    def can_read_notes(self, user_privileges: List[str]) -> bool:
        """Check if user can read notes."""
        return any(priv in self.PRIVILEGE_HIERARCHY["notes_read"] for priv in user_privileges)
    
    def can_write_notes(self, user_privileges: List[str]) -> bool:
        """Check if user can write/create notes."""
        return any(priv in self.PRIVILEGE_HIERARCHY["notes_write"] for priv in user_privileges)
    
    def can_edit_notes(self, user_privileges: List[str]) -> bool:
        """Check if user can edit notes."""
        return any(priv in self.PRIVILEGE_HIERARCHY["notes_edit"] for priv in user_privileges)
    
    def can_delete_notes(self, user_privileges: List[str]) -> bool:
        """Check if user can delete notes."""
        return any(priv in self.PRIVILEGE_HIERARCHY["notes_delete"] for priv in user_privileges)
    
    def can_export_notes(self, user_privileges: List[str]) -> bool:
        """Check if user can export notes."""
        return any(priv in self.PRIVILEGE_HIERARCHY["notes_export"] for priv in user_privileges)
    
    def can_search_notes(self, user_privileges: List[str]) -> bool:
        """Check if user can search notes."""
        return self.can_read_notes(user_privileges)
    
    def can_view_statistics(self, user_privileges: List[str]) -> bool:
        """Check if user can view notes statistics."""
        return any(priv in ["owner", "admin", "manager"] for priv in user_privileges)
    
    def validate_read_access(self, requesting_user: Dict[str, Any], target_user: Dict[str, Any], 
                           requesting_user_privileges: List[str]) -> None:
        """Validate that user can read notes for target user."""
        if not self.can_read_notes(requesting_user_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to read notes")
        
        # Check company access - owners can access across companies
        if 'owner' not in requesting_user_privileges:
            if requesting_user.get('company_id') != target_user.get('company_id'):
                raise CompanyMismatchError("Cannot access notes for users from different companies")
    
    def validate_write_access(self, author_user: Dict[str, Any], target_user: Dict[str, Any], 
                            author_privileges: List[str]) -> None:
        """Validate that user can write notes for target user."""
        if not self.can_write_notes(author_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to create notes")
        
        # Check company access - owners can write across companies
        if 'owner' not in author_privileges:
            if author_user.get('company_id') != target_user.get('company_id'):
                raise CompanyMismatchError("Cannot create notes for users from different companies")
    
    def validate_edit_access(self, editor_user: Dict[str, Any], note_author_uuid: str, 
                           editor_privileges: List[str]) -> None:
        """Validate that user can edit a specific note."""
        if not self.can_edit_notes(editor_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to edit notes")
        
        # Original author can edit (if they have edit privileges)
        if editor_user.get('uuid') == note_author_uuid:
            return
        
        # Only owners can edit others' notes
        if 'owner' not in editor_privileges:
            raise InsufficientPrivilegesError("Only note authors and owners can edit notes")
    
    def validate_delete_access(self, deleter_privileges: List[str]) -> None:
        """Validate that user can delete notes."""
        if not self.can_delete_notes(deleter_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to delete notes")
    
    def validate_export_access(self, exporter_privileges: List[str]) -> None:
        """Validate that user can export notes."""
        if not self.can_export_notes(exporter_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to export notes")
    
    def validate_search_access(self, searcher_privileges: List[str]) -> None:
        """Validate that user can search notes."""
        if not self.can_search_notes(searcher_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to search notes")
    
    def validate_statistics_access(self, requester_privileges: List[str]) -> None:
        """Validate that user can view statistics."""
        if not self.can_view_statistics(requester_privileges):
            raise InsufficientPrivilegesError("User lacks privileges to view statistics")
    
    def get_accessible_privileges(self, user_privileges: List[str]) -> Dict[str, bool]:
        """Get a dictionary of what privileges the user has for notes operations."""
        return {
            'can_read': self.can_read_notes(user_privileges),
            'can_write': self.can_write_notes(user_privileges),
            'can_edit': self.can_edit_notes(user_privileges),
            'can_delete': self.can_delete_notes(user_privileges),
            'can_export': self.can_export_notes(user_privileges),
            'can_search': self.can_search_notes(user_privileges),
            'can_view_statistics': self.can_view_statistics(user_privileges)
        }
    
    def log_access_attempt(self, operation: str, user_uuid: str, privileges: List[str], 
                          success: bool, reason: str = None) -> None:
        """Log access attempts for auditing purposes."""
        status = "SUCCESS" if success else "DENIED"
        log_msg = f"Notes {operation} - User: {user_uuid}, Privileges: {privileges}, Status: {status}"
        
        if reason:
            log_msg += f", Reason: {reason}"
        
        if success:
            logger.info(log_msg)
        else:
            logger.warning(log_msg)