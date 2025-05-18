# app/services/auth/Company_Storage/company_location.py
import time
import logging
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

class CompanyLocationManager:
    def __init__(self, company_storage):
        """
        Initialize location manager with reference to company storage
        
        Args:
            company_storage: Reference to the CompanyStorage instance
        """
        self.company_storage = company_storage
    
    def add_location(self, company_name: str, location: Dict, added_by: str) -> bool:
        """
        Add a location to a company
        
        Args:
            company_name: Name of the company
            location: Location details
            added_by: Email of the user adding the location
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.company_storage.can_user_manage_privileges(added_by, company_name):
            logger.warning(f"User {added_by} not authorized to add location")
            return False
        
        # Initialize locations array if not present
        if "locations" not in company:
            company["locations"] = []
        
        # Add timestamp and who added it
        location["added_by"] = added_by
        location["added_at"] = time.time()
        
        # Add the location
        company["locations"].append(location)
        
        return self.company_storage._save_companies()
    
    def update_location(self, company_name: str, location_index: int, location: Dict, updated_by: str) -> bool:
        """
        Update a location
        
        Args:
            company_name: Name of the company
            location_index: Index of the location to update
            location: Updated location details
            updated_by: Email of the user updating the location
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.company_storage.can_user_manage_privileges(updated_by, company_name):
            logger.warning(f"User {updated_by} not authorized to update location")
            return False
        
        # Check if locations array exists and index is valid
        if "locations" not in company or location_index >= len(company["locations"]):
            logger.warning(f"Location index {location_index} not found")
            return False
        
        # Preserve who originally added it
        original_location = company["locations"][location_index]
        location["added_by"] = original_location.get("added_by")
        location["added_at"] = original_location.get("added_at")
        
        # Add update info
        location["updated_by"] = updated_by
        location["updated_at"] = time.time()
        
        # Update the location
        company["locations"][location_index] = location
        
        return self.company_storage._save_companies()
    
    def remove_location(self, company_name: str, location_index: int, removed_by: str) -> bool:
        """
        Remove a location
        
        Args:
            company_name: Name of the company
            location_index: Index of the location to remove
            removed_by: Email of the user removing the location
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.company_storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.company_storage.can_user_manage_privileges(removed_by, company_name):
            logger.warning(f"User {removed_by} not authorized to remove location")
            return False
        
        # Check if locations array exists and index is valid
        if "locations" not in company or location_index >= len(company["locations"]):
            logger.warning(f"Location index {location_index} not found")
            return False
        
        # Remove the location
        company["locations"].pop(location_index)
        
        return self.company_storage._save_companies()