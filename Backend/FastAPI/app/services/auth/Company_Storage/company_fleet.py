# app/services/auth/Company_Storage/company_fleet.py
import logging
import time
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)

class CompanyFleetManager:
    def __init__(self, company_storage):
        """Initialize with reference to company storage"""
        self.company_storage = company_storage
    
    def add_fleet_category(self, company_name: str, fleet_category: Dict, added_by: str) -> bool:
        """
        Add a fleet category to a company
        
        Args:
            company_name: Name of the company
            fleet_category: Fleet category details
            added_by: Email of the user adding the fleet category
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.company_storage.can_user_manage_privileges(added_by, company_name):
            logger.warning(f"User {added_by} not authorized to add fleet category")
            return False
        
        # Initialize fleet_categories array if not present
        if "fleet_categories" not in company:
            company["fleet_categories"] = []
        
        # Add timestamp and who added it
        fleet_category["added_by"] = added_by
        fleet_category["added_at"] = time.time()
        
        # Add the fleet category
        company["fleet_categories"].append(fleet_category)
        
        return self.company_storage._save_companies()
    
    def update_fleet_category(self, company_name: str, category_index: int, fleet_category: Dict, updated_by: str) -> bool:
        """
        Update a fleet category
        
        Args:
            company_name: Name of the company
            category_index: Index of the fleet category to update
            fleet_category: Updated fleet category details
            updated_by: Email of the user updating the fleet category
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.company_storage.can_user_manage_privileges(updated_by, company_name):
            logger.warning(f"User {updated_by} not authorized to update fleet category")
            return False
        
        # Check if fleet_categories array exists and index is valid
        if "fleet_categories" not in company or category_index >= len(company["fleet_categories"]):
            logger.warning(f"Fleet category index {category_index} not found")
            return False
        
        # Preserve who originally added it
        original_category = company["fleet_categories"][category_index]
        fleet_category["added_by"] = original_category.get("added_by")
        fleet_category["added_at"] = original_category.get("added_at")
        
        # Add update info
        fleet_category["updated_by"] = updated_by
        fleet_category["updated_at"] = time.time()
        
        # Update the fleet category
        company["fleet_categories"][category_index] = fleet_category
        
        return self.company_storage._save_companies()
    
    def remove_fleet_category(self, company_name: str, category_index: int, removed_by: str) -> bool:
        """
        Remove a fleet category
        
        Args:
            company_name: Name of the company
            category_index: Index of the fleet category to remove
            removed_by: Email of the user removing the fleet category
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.company_storage.can_user_manage_privileges(removed_by, company_name):
            logger.warning(f"User {removed_by} not authorized to remove fleet category")
            return False
        
        # Check if fleet_categories array exists and index is valid
        if "fleet_categories" not in company or category_index >= len(company["fleet_categories"]):
            logger.warning(f"Fleet category index {category_index} not found")
            return False
        
        # Remove the fleet category
        company["fleet_categories"].pop(category_index)
        
        return self.company_storage._save_companies()