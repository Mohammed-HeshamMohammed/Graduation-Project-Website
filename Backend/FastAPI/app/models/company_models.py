"""
Company data models and validation utilities.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CompanyModels:
    """Company data models with validation and default values."""
    
    INDUSTRY_OPTIONS = [
        "Transportation", "Logistics", "Construction", "Delivery", "Other"
    ]
    
    COMPANY_SIZE_OPTIONS = [
        "Small (1–50 employees)",
        "Medium (51–200 employees)", 
        "Large (201–1000 employees)",
        "Enterprise (1000+ employees)"
    ]
    
    TIMEZONE_OPTIONS = [
        "GMT+0", "GMT+1", "GMT+2", "GMT+3 (Africa/Cairo)",
        "GMT+4", "GMT+5", "GMT+6", "GMT+7", "GMT+8", "GMT+9",
        "GMT+10", "GMT+11", "GMT+12", "GMT-1", "GMT-2", "GMT-3",
        "GMT-4", "GMT-5", "GMT-6", "GMT-7", "GMT-8", "GMT-9",
        "GMT-10", "GMT-11", "GMT-12"
    ]
    
    LOCATION_TYPE_OPTIONS = [
        "Headquarters", "Depot", "Garage", "Fuel Station", "Maintenance Hub"
    ]
    
    @staticmethod
    def validate_company_data(company_data):
        try:
            if not isinstance(company_data, dict):
                return False, "Company data must be a dictionary"
            
            required_fields = ["uuid", "company_name", "company_address", "industry", 
                             "company_size", "contact_phone", "contact_email", "timezone"]
            
            for field in required_fields:
                if field not in company_data or not company_data[field]:
                    return False, f"Missing or empty required field: {field}"
            
            if company_data["industry"] not in CompanyModels.INDUSTRY_OPTIONS:
                return False, f"Invalid industry option: {company_data['industry']}"
            
            if company_data["company_size"] not in CompanyModels.COMPANY_SIZE_OPTIONS:
                return False, f"Invalid company size option: {company_data['company_size']}"
            
            if company_data["timezone"] not in CompanyModels.TIMEZONE_OPTIONS:
                return False, f"Invalid timezone option: {company_data['timezone']}"
            
            return True, "Valid company data"
        except Exception as e:
            logger.error(f"validate_company_data: {type(e).__name__}: {e}")
            return False, str(e)
    
    @staticmethod
    def validate_business_hours(hours_data):
        try:
            if not isinstance(hours_data, dict):
                return False, "Business hours data must be a dictionary"
            
            required_fields = ["company_id", "start_time", "end_time", "working_days"]
            
            for field in required_fields:
                if field not in hours_data:
                    return False, f"Missing required field: {field}"
            
            working_days = hours_data["working_days"]
            if not isinstance(working_days, dict):
                return False, "Working days must be a dictionary"
            
            day_fields = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for day in day_fields:
                if day not in working_days or not isinstance(working_days[day], bool):
                    return False, f"Missing or invalid working day: {day}"
            
            return True, "Valid business hours data"
        except Exception as e:
            logger.error(f"validate_business_hours: {type(e).__name__}: {e}")
            return False, str(e)
    
    @staticmethod
    def validate_company_location(location_data):
        try:
            if not isinstance(location_data, dict):
                return False, "Location data must be a dictionary"
            
            required_fields = ["uuid", "company_id", "name", "address", "type"]
            
            for field in required_fields:
                if field not in location_data or not location_data[field]:
                    return False, f"Missing or empty required field: {field}"
            
            if location_data["type"] not in CompanyModels.LOCATION_TYPE_OPTIONS:
                return False, f"Invalid location type: {location_data['type']}"
            
            if "tags" in location_data and not isinstance(location_data["tags"], list):
                return False, "Tags must be a list"
            
            return True, "Valid location data"
        except Exception as e:
            logger.error(f"validate_company_location: {type(e).__name__}: {e}")
            return False, str(e)
    
    @staticmethod
    def create_default_company():
        return {
            "uuid": "",
            "company_name": "",
            "company_address": "",
            "logo": None,
            "industry": "",
            "company_size": "",
            "contact_phone": "",
            "contact_email": "",
            "website": "",
            "timezone": "GMT+3 (Africa/Cairo)"
        }
    
    @staticmethod
    def create_default_business_hours():
        return {
            "company_id": "",
            "start_time": "09:00",
            "end_time": "17:00",
            "working_days": {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": False,
                "sunday": False
            }
        }
    
    @staticmethod
    def create_default_location():
        return {
            "uuid": "",
            "company_id": "",
            "name": "",
            "address": "",
            "type": "Headquarters",
            "tags": []
        }
    
    @staticmethod
    def sanitize_company_data(company_data):
        try:
            if not isinstance(company_data, dict):
                return None
            
            sanitized = company_data.copy()
            
            string_fields = ["company_name", "company_address", "contact_phone", 
                           "contact_email", "website", "industry", "company_size", "timezone"]
            
            for field in string_fields:
                if field in sanitized and isinstance(sanitized[field], str):
                    sanitized[field] = sanitized[field].strip()
            
            if "contact_email" in sanitized:
                sanitized["contact_email"] = sanitized["contact_email"].lower()
            
            return sanitized
        except Exception as e:
            logger.error(f"sanitize_company_data: {type(e).__name__}: {e}")
            return None