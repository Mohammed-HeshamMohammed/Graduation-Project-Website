"""
Company storage class for managing company data with encryption and access control.
"""

import logging
from typing import Dict, List, Optional, Any
from .base_storage import BaseStorage
from .access_control import AccessControlMixin
from .company_file_handler import CompanyFileHandler

logger = logging.getLogger(__name__)


class CompanyStorage(BaseStorage, AccessControlMixin):
    """Storage class for company data management with encryption and access control."""
    
    def __init__(self):
        BaseStorage.__init__(self)
        AccessControlMixin.__init__(self)
        
        self.company_file_handler = CompanyFileHandler()
        
        self.companies = self.company_file_handler.load_companies()
        self.business_hours = self.company_file_handler.load_business_hours()
        self.company_locations = self.company_file_handler.load_company_locations()
    
    def _get_company(self, key, value):
        if not self.validate_input(value, str, key):
            return None
        for company in self.companies.values():
            if isinstance(company, dict) and company.get(key) == value:
                return company
        return None

    def get_company_by_uuid(self, uuid):
        try:
            return self._get_company('uuid', uuid)
        except Exception as e:
            logger.error(f"get_company_by_uuid: {type(e).__name__}: {e}")
            return None

    def get_company_by_name(self, company_name):
        try:
            if not self.validate_input(company_name, str, "company_name"):
                return None
            return self._get_company('company_name', company_name.strip())
        except Exception as e:
            logger.error(f"get_company_by_name: {type(e).__name__}: {e}")
            return None

    def get_all_companies(self):
        try:
            return self.companies.copy()
        except Exception as e:
            logger.error(f"get_all_companies: {type(e).__name__}: {e}")
            return {}

    def save_company(self, company):
        try:
            if not isinstance(company, dict) or "uuid" not in company:
                return False
            uuid = company["uuid"]
            if not uuid:
                return False
            self.companies[uuid] = company.copy()
            if self.company_file_handler.save_companies(self.companies):
                return True
            del self.companies[uuid]
            return False
        except Exception as e:
            logger.error(f"save_company: {type(e).__name__}: {e}")
            return False

    def update_company(self, company):
        try:
            if not isinstance(company, dict) or "uuid" not in company:
                return False
            uuid = company["uuid"]
            if not uuid or uuid not in self.companies:
                return False
            original = self.companies[uuid].copy()
            self.companies[uuid] = company.copy()
            if self.company_file_handler.save_companies(self.companies):
                return True
            self.companies[uuid] = original
            return False
        except Exception as e:
            logger.error(f"update_company: {type(e).__name__}: {e}")
            return False

    def delete_company(self, uuid):
        try:
            if not uuid or uuid not in self.companies:
                return False
            deleted_company = self.companies[uuid].copy()
            del self.companies[uuid]
            if not self.company_file_handler.save_companies(self.companies):
                self.companies[uuid] = deleted_company
                return False
            self.company_file_handler.cleanup_company_data(uuid, self.business_hours, self.company_locations)
            return True
        except Exception as e:
            logger.error(f"delete_company: {type(e).__name__}: {e}")
            return False

    def get_business_hours(self, company_id):
        try:
            return self.business_hours.get(company_id, {})
        except Exception as e:
            logger.error(f"get_business_hours: {type(e).__name__}: {e}")
            return {}

    def save_business_hours(self, company_id, hours):
        try:
            if not self.validate_input(company_id, str, "company_id") or not isinstance(hours, dict):
                return False
            self.business_hours[company_id] = hours.copy()
            if self.company_file_handler.save_business_hours(self.business_hours):
                return True
            del self.business_hours[company_id]
            return False
        except Exception as e:
            logger.error(f"save_business_hours: {type(e).__name__}: {e}")
            return False

    def get_company_locations(self, company_id):
        try:
            return self.company_locations.get(company_id, [])
        except Exception as e:
            logger.error(f"get_company_locations: {type(e).__name__}: {e}")
            return []

    def save_company_locations(self, company_id, locations):
        try:
            if not self.validate_input(company_id, str, "company_id") or not isinstance(locations, list):
                return False
            self.company_locations[company_id] = locations.copy()
            if self.company_file_handler.save_company_locations(self.company_locations):
                return True
            del self.company_locations[company_id]
            return False
        except Exception as e:
            logger.error(f"save_company_locations: {type(e).__name__}: {e}")
            return False

    def get_location_by_uuid(self, location_uuid):
        try:
            for locations in self.company_locations.values():
                if isinstance(locations, list):
                    for location in locations:
                        if isinstance(location, dict) and location.get('uuid') == location_uuid:
                            return location
            return None
        except Exception as e:
            logger.error(f"get_location_by_uuid: {type(e).__name__}: {e}")
            return None

    def add_company_location(self, company_id, location):
        try:
            if not self.validate_input(company_id, str, "company_id") or not isinstance(location, dict):
                return False
            if company_id not in self.company_locations:
                self.company_locations[company_id] = []
            self.company_locations[company_id].append(location.copy())
            if self.company_file_handler.save_company_locations(self.company_locations):
                return True
            self.company_locations[company_id].pop()
            return False
        except Exception as e:
            logger.error(f"add_company_location: {type(e).__name__}: {e}")
            return False

    def update_company_location(self, company_id, location_uuid, updated_location):
        try:
            if not self.validate_input(company_id, str, "company_id") or not isinstance(updated_location, dict):
                return False
            locations = self.company_locations.get(company_id, [])
            for i, location in enumerate(locations):
                if isinstance(location, dict) and location.get('uuid') == location_uuid:
                    original = location.copy()
                    locations[i] = updated_location.copy()
                    if self.company_file_handler.save_company_locations(self.company_locations):
                        return True
                    locations[i] = original
                    return False
            return False
        except Exception as e:
            logger.error(f"update_company_location: {type(e).__name__}: {e}")
            return False

    def delete_company_location(self, company_id, location_uuid):
        try:
            if not self.validate_input(company_id, str, "company_id"):
                return False
            locations = self.company_locations.get(company_id, [])
            for i, location in enumerate(locations):
                if isinstance(location, dict) and location.get('uuid') == location_uuid:
                    deleted_location = locations.pop(i)
                    if self.company_file_handler.save_company_locations(self.company_locations):
                        return True
                    locations.insert(i, deleted_location)
                    return False
            return False
        except Exception as e:
            logger.error(f"delete_company_location: {type(e).__name__}: {e}")
            return False

    def get_company_storage_stats(self):
        try:
            file_stats = self.company_file_handler.get_file_stats()
            return {
                'companies_count': len(self.companies),
                'business_hours_count': len(self.business_hours),
                'company_locations_count': sum(len(locs) for locs in self.company_locations.values()),
                'file_stats': file_stats,
                'memory_usage': {
                    'companies_keys': list(self.companies.keys())[:5],
                    'business_hours_keys': list(self.business_hours.keys())[:5],
                    'company_locations_keys': list(self.company_locations.keys())[:5]
                }
            }
        except Exception as e:
            logger.error(f"get_company_storage_stats: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'companies_count': 0,
                'business_hours_count': 0,
                'company_locations_count': 0
            }