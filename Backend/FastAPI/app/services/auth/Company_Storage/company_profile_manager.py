# app/services/auth/company_profile_manager.py
import logging
from typing import Dict, Any
import time

logger = logging.getLogger(__name__)

class CompanyProfileManager:
    """
    Manages company profile details and business hours
    """
    
    def __init__(self, storage):
        """
        Initialize with a reference to the CompanyStorage
        
        Args:
            storage: Reference to the CompanyStorage instance
        """
        self.storage = storage
    
    def get_company_details(self, company_name: str) -> Dict:
        """
        Get company details
        
        Args:
            company_name: Name of the company
            
        Returns:
            Dict: Company details or empty dict if not found
        """
        company = self.storage.get_company_by_name(company_name)
        if not company:
            return {}
        
        return {
            "company_details": company.get("company_details", {}),
            "business_hours": company.get("business_hours", {}),
            "locations": company.get("locations", []),
            "fleet_categories": company.get("fleet_categories", [])
        }
    
    def update_company_details(self, company_name: str, details: Dict, updated_by: str) -> bool:
        """
        Update company details
        
        Args:
            company_name: Name of the company
            details: Dictionary of company details
            updated_by: Email of the user updating details
            
        Returns:
            bool: True if successful, False otherwise
        """
        company = self.storage.get_company_by_name(company_name)
        if not company:
            logger.warning(f"Company {company_name} does not exist")
            return False
        
        # Check if user has permissions to update company details
        if not self.storage.can_user_manage_privileges(updated_by, company_name):
            logger.warning(f"User {updated_by} not authorized to update company details")
            return False
        
        # Update the company details section
        if "company_details" in details:
            company["company_details"] = details["company_details"]
            company["company_details"]["updated_by"] = updated_by
            company["company_details"]["updated_at"] = time.time()
        
        # Update the business hours section
        if "business_hours" in details:
            company["business_hours"] = details["business_hours"]
            company["business_hours"]["updated_by"] = updated_by
            company["business_hours"]["updated_at"] = time.time()
        
        # Save the update
        return self.storage._save_companies()
    
    def get_company_schema(self) -> Dict:
        """
        Get the company details schema
        
        Returns:
            Dict: Schema for company details
        """
        return {
            "companyDetails": {
                "company_name": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "logo": {
                    "type": "file",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "industry": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": True,
                    "options": ["Transportation", "Logistics", "Construction", "Delivery", "Other"]
                },
                "company_size": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": True,
                    "options": [
                        "Small (1–50 employees)",
                        "Medium (51–200 employees)",
                        "Large (201–1000 employees)",
                        "Enterprise (1000+ employees)"
                    ]
                },
                "contact_phone": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "contact_email": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "website": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "timezone": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": True,
                    "options": ["GMT+0", "GMT+1", "GMT+2", "GMT+3 (Africa/Cairo)", "GMT+4", "..."]
                }
            },
            "businessHours": {
                "start_time": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "end_time": {
                    "type": "string",
                    "is_boolean": False,
                    "is_option_restricted": False
                },
                "working_days": {
                    "type": "object",
                    "days": {
                        "monday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False},
                        "tuesday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False},
                        "wednesday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False},
                        "thursday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False},
                        "friday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False},
                        "saturday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False},
                        "sunday": {"type": "boolean", "is_boolean": True, "is_option_restricted": False}
                    }
                }
            },
            "locations": {
                "type": "array",
                "item_structure": {
                    "name": {
                        "type": "string",
                        "is_boolean": False,
                        "is_option_restricted": False
                    },
                    "address": {
                        "type": "string",
                        "is_boolean": False,
                        "is_option_restricted": False
                    },
                    "type": {
                        "type": "string",
                        "is_boolean": False,
                        "is_option_restricted": True,
                        "options": ["Headquarters", "Depot", "Garage", "Fuel Station", "Maintenance Hub"]
                    },
                    "tags": {
                        "type": "array",
                        "is_boolean": False,
                        "is_option_restricted": False
                    }
                }
            },
            "fleetCategories": {
                "type": "array",
                "item_structure": {
                    "type": {
                        "type": "string",
                        "is_boolean": False,
                        "is_option_restricted": True,
                        "options": [
                            "Cargo Trucks",
                            "Delivery Vans",
                            "Buses",
                            "Taxis",
                            "Emergency Vehicles",
                            "Utility Vehicles",
                            "Construction Vehicles",
                            "Motorbikes/Scooters",
                            "Electric Vehicles",
                            "Mixed Fleet"
                        ]
                    },
                    "specs": {
                        "dynamic": True,
                        "example_fields": {
                            "refrigeration": {
                                "type": "boolean",
                                "is_boolean": True,
                                "is_option_restricted": False
                            },
                            "max_load_tons": {
                                "type": "number",
                                "is_boolean": False,
                                "is_option_restricted": False
                            },
                            "battery_capacity_kwh": {
                                "type": "number",
                                "is_boolean": False,
                                "is_option_restricted": False
                            }
                        }
                    }
                }
            }
        }