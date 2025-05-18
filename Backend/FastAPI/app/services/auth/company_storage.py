# app/services/auth/company_storage.py
import os
from pathlib import Path
import logging
from typing import List, Dict, Optional

from app.config import settings
from app.services.auth.user_privileges import UserPrivilege

from app.services.auth.Company_Storage.company_storage_manager import CompanyStorageManager
from app.services.auth.Company_Storage.company_registry_manager import CompanyRegistryManager
from app.services.auth.Company_Storage.company_member_manager import CompanyMemberManager
from app.services.auth.Company_Storage.company_profile_manager import CompanyProfileManager
from app.services.auth.Company_Storage.company_location import CompanyLocationManager
from app.services.auth.Company_Storage.company_fleet import CompanyFleetManager

# Configure logging
logger = logging.getLogger(__name__)

class CompanyStorage:
    """
    Main class for managing company data storage and operations
    
    Acts as a facade for all specialized manager classes
    """
    def __init__(self):
        """Initialize storage and component managers"""
        self.data_dir = Path(settings.DATA_DIR)
        
        # Make UserPrivilege accessible to manager classes
        self.UserPrivilege = UserPrivilege
        
        # Initialize storage manager and load companies
        self.storage_manager = CompanyStorageManager(self.data_dir)
        self.companies = self.storage_manager.load_companies()
        
        # Initialize all component managers
        self.registry_manager = CompanyRegistryManager(self)
        self.member_manager = CompanyMemberManager(self)
        self.profile_manager = CompanyProfileManager(self)
        self.location_manager = CompanyLocationManager(self)
        self.fleet_manager = CompanyFleetManager(self)
    
    def _save_companies(self) -> bool:
        """Save companies to storage via storage manager"""
        return self.storage_manager.save_companies(self.companies)
    
    # ============== REGISTRY MANAGER DELEGATIONS ==============
    
    def get_company_by_name(self, company_name: str) -> Optional[Dict]:
        """Get a company by name - delegated to registry manager"""
        return self.registry_manager.get_company_by_name(company_name)
    
    def is_company_registered(self, company_name: str) -> bool:
        """Check if a company is registered - delegated to registry manager"""
        return self.registry_manager.is_company_registered(company_name)
    
    def add_company(self, company_name: str, owner_email: str) -> bool:
        """Add a new company - delegated to registry manager"""
        return self.registry_manager.add_company(company_name, owner_email)
    
    # ============== MEMBER MANAGER DELEGATIONS ==============
    
    def get_user_company_privileges(self, email: str, company_name: str) -> List[str]:
        """Get user privileges - delegated to member manager"""
        return self.member_manager.get_user_company_privileges(email, company_name)
    
    def is_user_authorized_for_company(self, email: str, company_name: str) -> bool:
        """Check if user is authorized - delegated to member manager"""
        return self.member_manager.is_user_authorized_for_company(email, company_name)
    
    def can_user_add_members(self, email: str, company_name: str) -> bool:
        """Check if user can add members - delegated to member manager"""
        return self.member_manager.can_user_add_members(email, company_name)
    
    def can_user_remove_members(self, email: str, company_name: str) -> bool:
        """Check if user can remove members - delegated to member manager"""
        return self.member_manager.can_user_remove_members(email, company_name)
    
    def can_user_manage_privileges(self, email: str, company_name: str) -> bool:
        """Check if user can manage privileges - delegated to member manager"""
        return self.member_manager.can_user_manage_privileges(email, company_name)
    
    def is_user_owner(self, email: str, company_name: str) -> bool:
        """Check if user is owner - delegated to member manager"""
        return self.member_manager.is_user_owner(email, company_name)
    
    def add_member(self, company_name: str, email: str, added_by: str, privileges: List[str] = None) -> bool:
        """Add a member - delegated to member manager"""
        return self.member_manager.add_member(company_name, email, added_by, privileges)
    
    def remove_member(self, company_name: str, email: str, removed_by: str) -> bool:
        """Remove a member - delegated to member manager"""
        return self.member_manager.remove_member(company_name, email, removed_by)
    
    def update_member_privileges(self, company_name: str, email: str, privileges: List[str], updated_by: str) -> bool:
        """Update member privileges - delegated to member manager"""
        return self.member_manager.update_member_privileges(company_name, email, privileges, updated_by)
    
    def get_company_members(self, company_name: str) -> Dict:
        """Get company members - delegated to member manager"""
        return self.member_manager.get_company_members(company_name)
    
    # ============== PROFILE MANAGER DELEGATIONS ==============
    
    def get_company_details(self, company_name: str) -> Dict:
        """Get company details - delegated to profile manager"""
        return self.profile_manager.get_company_details(company_name)
    
    def update_company_details(self, company_name: str, details: Dict, updated_by: str) -> bool:
        """Update company details - delegated to profile manager"""
        return self.profile_manager.update_company_details(company_name, details, updated_by)
    
    def get_company_schema(self) -> Dict:
        """Get company schema - delegated to profile manager"""
        return self.profile_manager.get_company_schema()
    
    # ============== LOCATION MANAGER DELEGATIONS ==============
    
    def add_location(self, company_name: str, location: Dict, added_by: str) -> bool:
        """Add a location - delegated to location manager"""
        return self.location_manager.add_location(company_name, location, added_by)
    
    def update_location(self, company_name: str, location_index: int, location: Dict, updated_by: str) -> bool:
        """Update a location - delegated to location manager"""
        return self.location_manager.update_location(company_name, location_index, location, updated_by)
    
    def remove_location(self, company_name: str, location_index: int, removed_by: str) -> bool:
        """Remove a location - delegated to location manager"""
        return self.location_manager.remove_location(company_name, location_index, removed_by)
    
    # ============== FLEET MANAGER DELEGATIONS ==============
    
    def add_fleet_category(self, company_name: str, fleet_category: Dict, added_by: str) -> bool:
        """Add a fleet category - delegated to fleet manager"""
        return self.fleet_manager.add_fleet_category(company_name, fleet_category, added_by)
    
    def update_fleet_category(self, company_name: str, category_index: int, fleet_category: Dict, updated_by: str) -> bool:
        """Update a fleet category - delegated to fleet manager"""
        return self.fleet_manager.update_fleet_category(company_name, category_index, fleet_category, updated_by)
    
    def remove_fleet_category(self, company_name: str, category_index: int, removed_by: str) -> bool:
        """Remove a fleet category - delegated to fleet manager"""
        return self.fleet_manager.remove_fleet_category(company_name, category_index, removed_by)