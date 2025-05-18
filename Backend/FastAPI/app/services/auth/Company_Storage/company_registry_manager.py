# app/services/auth/Company_Storage/company_registry_manager.py
import logging
import time
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

class CompanyRegistryManager:
    def __init__(self, company_storage):
        """Initialize with reference to company storage"""
        self.company_storage = company_storage
    
    def get_company_by_name(self, company_name: str) -> Optional[Dict]:
        """
        Get a company by name
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dict or None: Company data or None if not found
        """
        # Use case-insensitive comparison for company names
        company_name_lower = company_name.lower() if company_name else None
        
        # Look for the company with case-insensitive matching
        for name, company in self.company_storage.companies.items():
            if name.lower() == company_name_lower:
                return company
        return None
    
    def is_company_registered(self, company_name: str) -> bool:
        """
        Check if a company is already registered
        
        Args:
            company_name: Name of the company
            
        Returns:
            bool: True if company exists, False otherwise
        """
        return self.get_company_by_name(company_name) is not None
    
    def add_company(self, company_name: str, owner_email: str) -> bool:
        """
        Add a new company with its owner
        
        Args:
            company_name: Name of the company
            owner_email: Email of the user who registered the company
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check for valid company name
        if not company_name:
            logger.warning("Attempted to add company with no name")
            return False
            
        # Check if company already exists
        if self.is_company_registered(company_name):
            logger.warning(f"Company {company_name} already exists")
            return False
        
        # Add the company with members dictionary containing privileges
        self.company_storage.companies[company_name] = {
            "name": company_name,
            "owner_email": owner_email,
            "members": {
                owner_email: {
                    "privileges": [self.company_storage.UserPrivilege.OWNER],
                    "added_by": None,  # Owner added themselves
                    "added_at": time.time()
                }
            },
            "created_at": time.time(),
            # Initialize empty profile sections that can be filled later
            "company_details": {},
            "business_hours": {},
            "locations": [],
            "fleet_categories": []
        }
        
        # Save to storage
        return self.company_storage._save_companies()