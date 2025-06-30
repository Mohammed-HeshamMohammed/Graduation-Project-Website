"""
File handler for managing company-related encrypted storage files.
"""

import os
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List
from app.config import settings
from .base_storage import BaseStorage

logger = logging.getLogger(__name__)


class CompanyFileHandler(BaseStorage):
    """Handler for managing company storage files with thread safety."""
    
    def __init__(self):
        super().__init__()
        
        self._lock = threading.RLock()
        
        self.companies_path = self.data_dir / "companies.enc"
        self.business_hours_path = self.data_dir / "business_hours.enc"
        self.company_locations_path = self.data_dir / "company_locations.enc"
    
    def load_companies(self):
        with self._lock:
            try:
                companies = self.load_encrypted_data(self.companies_path, "companies")
                logger.info(f"Loaded {len(companies)} companies from storage")
                return companies
            except Exception as e:
                logger.error(f"load_companies: {type(e).__name__}: {e}")
                return {}
    
    def save_companies(self, companies):
        with self._lock:
            try:
                if not isinstance(companies, dict):
                    return False
                success = self.save_encrypted_data(companies, self.companies_path, "companies")
                if success:
                    logger.info(f"Successfully saved {len(companies)} companies")
                return success
            except Exception as e:
                logger.error(f"save_companies: {type(e).__name__}: {e}")
                return False
    
    def load_business_hours(self):
        with self._lock:
            try:
                business_hours = self.load_encrypted_data(self.business_hours_path, "business_hours")
                logger.info(f"Loaded business hours for {len(business_hours)} companies")
                return business_hours
            except Exception as e:
                logger.error(f"load_business_hours: {type(e).__name__}: {e}")
                return {}
    
    def save_business_hours(self, business_hours):
        with self._lock:
            try:
                if not isinstance(business_hours, dict):
                    return False
                success = self.save_encrypted_data(business_hours, self.business_hours_path, "business_hours")
                if success:
                    logger.info(f"Successfully saved business hours for {len(business_hours)} companies")
                return success
            except Exception as e:
                logger.error(f"save_business_hours: {type(e).__name__}: {e}")
                return False
    
    def load_company_locations(self):
        with self._lock:
            try:
                company_locations = self.load_encrypted_data(self.company_locations_path, "company_locations")
                logger.info(f"Loaded locations for {len(company_locations)} companies")
                return company_locations
            except Exception as e:
                logger.error(f"load_company_locations: {type(e).__name__}: {e}")
                return {}
    
    def save_company_locations(self, company_locations):
        with self._lock:
            try:
                if not isinstance(company_locations, dict):
                    return False
                success = self.save_encrypted_data(company_locations, self.company_locations_path, "company_locations")
                if success:
                    total_locations = sum(len(locs) for locs in company_locations.values() if isinstance(locs, list))
                    logger.info(f"Successfully saved {total_locations} locations for {len(company_locations)} companies")
                return success
            except Exception as e:
                logger.error(f"save_company_locations: {type(e).__name__}: {e}")
                return False
    
    def cleanup_company_data(self, company_uuid, business_hours, company_locations):
        with self._lock:
            try:
                errors = []
                
                if company_uuid in business_hours:
                    del business_hours[company_uuid]
                    if not self.save_business_hours(business_hours):
                        errors.append("Failed to save business hours")
                
                if company_uuid in company_locations:
                    del company_locations[company_uuid]
                    if not self.save_company_locations(company_locations):
                        errors.append("Failed to save company locations")
                
                if errors:
                    msg = f"Partial cleanup failure for company {company_uuid}: {'; '.join(errors)}"
                    logger.warning(msg)
                    return False
                else:
                    logger.info(f"Successfully cleaned up data for deleted company: {company_uuid}")
                    return True
            except Exception as e:
                logger.error(f"Error cleaning up company data for {company_uuid}: {type(e).__name__}: {e}")
                return False
    
    def get_file_stats(self):
        with self._lock:
            stats = {}
            
            files = {
                'companies': self.companies_path,
                'business_hours': self.business_hours_path,
                'company_locations': self.company_locations_path
            }
            
            for file_type, file_path in files.items():
                try:
                    if file_path.exists():
                        stat = file_path.stat()
                        stats[file_type] = {
                            'exists': True,
                            'size_bytes': stat.st_size,
                            'modified_time': stat.st_mtime,
                            'readable': os.access(file_path, os.R_OK),
                            'writable': os.access(file_path, os.W_OK)
                        }
                    else:
                        stats[file_type] = {
                            'exists': False,
                            'size_bytes': 0,
                            'modified_time': None,
                            'readable': False,
                            'writable': False
                        }
                except Exception as e:
                    logger.error(f"Error getting stats for {file_type}: {e}")
                    stats[file_type] = {
                        'exists': False,
                        'error': str(e)
                    }
            
            return stats