# app/services/auth/Company_Storage/company_member_manager.py
import logging
import time
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)

class CompanyMemberManager:
    def __init__(self, company_storage):
        """Initialize with reference to company storage"""
        self.company_storage = company_storage
    
    def get_user_company_privileges(self, email: str, company_name: str) -> List[str]:
        """
        Get a user's privileges for a company
        
        Args:
            email: Email of the user
            company_name: Name of the company
        
        Returns:
            List[str]: List of privileges, empty if not found
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company or "members" not in company:
            return []
        
        member_info = company["members"].get(email)
        if not member_info:
            return []
        
        return member_info.get("privileges", [])
    
    def is_user_authorized_for_company(self, email: str, company_name: str) -> bool:
        """
        Check if a user is a member of a company
        
        Args:
            email: Email of the user
            company_name: Name of the company
        
        Returns:
            bool: True if authorized, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company or "members" not in company:
            return False
        
        # Check if user is in the members dictionary
        return email in company["members"]
    
    def can_user_add_members(self, email: str, company_name: str) -> bool:
        """
        Check if a user can add members to a company
        
        Args:
            email: Email of the user
            company_name: Name of the company
        
        Returns:
            bool: True if can add, False otherwise
        """
        privileges = self.get_user_company_privileges(email, company_name)
        return any(priv in privileges for priv in 
                  [self.company_storage.UserPrivilege.OWNER, 
                   self.company_storage.UserPrivilege.ADMIN, 
                   self.company_storage.UserPrivilege.ADD_MEMBERS])
    
    def can_user_remove_members(self, email: str, company_name: str) -> bool:
        """
        Check if a user can remove members from a company
        
        Args:
            email: Email of the user
            company_name: Name of the company
        
        Returns:
            bool: True if can remove, False otherwise
        """
        privileges = self.get_user_company_privileges(email, company_name)
        return any(priv in privileges for priv in 
                  [self.company_storage.UserPrivilege.OWNER, 
                   self.company_storage.UserPrivilege.ADMIN, 
                   self.company_storage.UserPrivilege.REMOVE_MEMBERS])
    
    def can_user_manage_privileges(self, email: str, company_name: str) -> bool:
        """
        Check if a user can manage privileges of other users
        
        Args:
            email: Email of the user
            company_name: Name of the company
        
        Returns:
            bool: True if can manage privileges, False otherwise
        """
        privileges = self.get_user_company_privileges(email, company_name)
        return any(priv in privileges for priv in 
                  [self.company_storage.UserPrivilege.OWNER, 
                   self.company_storage.UserPrivilege.ADMIN])
    
    def is_user_owner(self, email: str, company_name: str) -> bool:
        """
        Check if a user is the owner of a company
        
        Args:
            email: Email of the user
            company_name: Name of the company
        
        Returns:
            bool: True if owner, False otherwise
        """
        privileges = self.get_user_company_privileges(email, company_name)
        return self.company_storage.UserPrivilege.OWNER in privileges
    
    def add_member(self, company_name: str, email: str, added_by: str, privileges: List[str] = None) -> bool:
        """
        Add a member to a company
        
        Args:
            company_name: Name of the company
            email: Email of the user to add
            added_by: Email of the user adding the member
            privileges: List of privileges to assign (default is [MEMBER])
        
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if the person adding is allowed to add users
        if not self.can_user_add_members(added_by, company_name):
            logger.warning(f"User {added_by} not authorized to add members to company {company_name}")
            return False
        
        # Use default privileges if none provided
        if not privileges:
            privileges = [self.company_storage.UserPrivilege.MEMBER]
        else:
            # Filter out invalid privileges
            privileges = [p for p in privileges if self.company_storage.UserPrivilege.is_valid_privilege(p)]
            if not privileges:
                privileges = [self.company_storage.UserPrivilege.MEMBER]
        
        # Ensure only owners/admins can add admins
        if self.company_storage.UserPrivilege.ADMIN in privileges and not self.can_user_manage_privileges(added_by, company_name):
            logger.warning(f"User {added_by} not authorized to add admin to company {company_name}")
            return False
            
        # Prevent adding OWNER privilege (there can be only one owner)
        if self.company_storage.UserPrivilege.OWNER in privileges:
            logger.warning(f"Cannot add OWNER privilege - {company_name} already has an owner")
            privileges.remove(self.company_storage.UserPrivilege.OWNER)
            
        # Initialize members dict if not present
        if "members" not in company:
            company["members"] = {}
        
        # Add member or update privileges if already exists
        company["members"][email] = {
            "privileges": privileges,
            "added_by": added_by,
            "added_at": time.time()
        }
        
        # Save to storage
        return self.company_storage._save_companies()
    
    def remove_member(self, company_name: str, email: str, removed_by: str) -> bool:
        """
        Remove a member from a company
        
        Args:
            company_name: Name of the company
            email: Email of the user to remove
            removed_by: Email of the user removing the member
        
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company or "members" not in company:
            logger.warning(f"Company {company_name} does not exist or has no members")
            return False
        
        # Check if the person removing is allowed to remove users
        if not self.can_user_remove_members(removed_by, company_name):
            logger.warning(f"User {removed_by} not authorized to remove members from company {company_name}")
            return False
        
        # Check if the user to be removed exists
        if email not in company["members"]:
            logger.warning(f"User {email} not found in company {company_name}")
            return False
        
        # Cannot remove the owner
        if self.is_user_owner(email, company_name):
            logger.warning(f"Cannot remove owner {email} from company {company_name}")
            return False
        
        # Cannot remove yourself unless you're owner
        if email == removed_by and not self.is_user_owner(removed_by, company_name):
            logger.warning(f"User {removed_by} cannot remove themselves unless they are owner")
            return False
        
        # Remove the member
        del company["members"][email]
        
        # Save to storage
        return self.company_storage._save_companies()
    
    def update_member_privileges(self, company_name: str, email: str, privileges: List[str], updated_by: str) -> bool:
        """
        Update a member's privileges
        Args:
            company_name: Name of the company
            email: Email of the user to update
            privileges: New list of privileges
            updated_by: Email of the user updating privileges
        Returns: bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company or "members" not in company:
            logger.warning(f"Company {company_name} does not exist or has no members")
            return False
        
        # Check if the person updating is allowed to manage privileges
        if not self.can_user_manage_privileges(updated_by, company_name):
            logger.warning(f"User {updated_by} not authorized to manage privileges in company {company_name}")
            return False
        
        # Check if the user to be updated exists
        if email not in company["members"]:
            logger.warning(f"User {email} not found in company {company_name}")
            return False
        
        # Cannot modify owner's privileges
        if self.is_user_owner(email, company_name) and updated_by != email:
            logger.warning(f"Cannot modify owner privileges for {email} in company {company_name}")
            return False
        
        # Validate and filter privileges
        valid_privileges = [p for p in privileges if self.company_storage.UserPrivilege.is_valid_privilege(p)]
        if not valid_privileges:
            valid_privileges = [self.company_storage.UserPrivilege.MEMBER]
        
        # Preserve OWNER privilege if it was there
        if self.is_user_owner(email, company_name):
            if self.company_storage.UserPrivilege.OWNER not in valid_privileges:
                valid_privileges.append(self.company_storage.UserPrivilege.OWNER)
        # Or ensure it's not added if it wasn't there
        elif self.company_storage.UserPrivilege.OWNER in valid_privileges:
            valid_privileges.remove(self.company_storage.UserPrivilege.OWNER)
        
        # Update the privileges
        company["members"][email]["privileges"] = valid_privileges
        company["members"][email]["updated_by"] = updated_by
        company["members"][email]["updated_at"] = time.time()
        
        # Save to storage
        return self.company_storage._save_companies()
    
    def get_company_members(self, company_name: str) -> Dict:
        """
        Get all members of a company with their privileges
        Args: company_name: Name of the company
        Returns: Dict: Dictionary of members and their information, empty if company not found
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company or "members" not in company:
            return {}
        
        return company["members"]