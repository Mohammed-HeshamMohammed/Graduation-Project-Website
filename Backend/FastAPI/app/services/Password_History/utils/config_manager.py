# File: Password_History/utils/config_manager.py
"""Configuration management for password history policies"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class PasswordHistoryPolicy:
    """Password history policy configuration"""
    default_max_history: int = 5
    minimum_max_history: int = 1
    maximum_max_history: int = 50
    enable_encryption: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    backup_enabled: bool = True
    backup_retention_count: int = 10
    auto_backup_interval: int = 86400  # 24 hours
    audit_enabled: bool = True
    audit_retention_days: int = 90
    concurrency_max_retries: int = 3
    concurrency_retry_delay: float = 0.1
    enable_company_isolation: bool = True
    allow_admin_bypass: bool = False
    require_admin_approval_for_bypass: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PasswordHistoryPolicy':
        """Create from dictionary"""
        # Filter out unknown keys
        known_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

class ConfigManager:
    """Manager for password history configuration and policies"""
    
    def __init__(self, config_data: Dict[str, Any] = None, config_file: str = None):
        self.config_file = Path(config_file) if config_file else None
        self._config_data = config_data or {}
        self._policy_cache = {}
        
        # Load from file if specified
        if self.config_file and self.config_file.exists():
            self._load_from_file()
        
        # Create default policy
        self.default_policy = PasswordHistoryPolicy()
        self._merge_config_with_policy()
        
        logger.info("Configuration manager initialized")
    
    def _load_from_file(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
            
            # Merge with existing config
            self._config_data.update(file_config)
            logger.info(f"Loaded configuration from {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error loading configuration from file: {e}")
    
    def _merge_config_with_policy(self):
        """Merge configuration data with default policy"""
        if 'password_history_policy' in self._config_data:
            policy_data = self._config_data['password_history_policy']
            self.default_policy = PasswordHistoryPolicy.from_dict(policy_data)
    
    def get_policy(self, company_uuid: str = None) -> PasswordHistoryPolicy:
        """Get policy for a specific company or default"""
        if company_uuid is None:
            return self.default_policy
        
        # Check cache first
        if company_uuid in self._policy_cache:
            return self._policy_cache[company_uuid]
        
        # Look for company-specific policy in config
        company_policies = self._config_data.get('company_policies', {})
        
        if company_uuid in company_policies:
            try:
                company_policy_data = company_policies[company_uuid]
                # Start with default and override with company-specific settings
                merged_data = self.default_policy.to_dict()
                merged_data.update(company_policy_data)
                
                policy = PasswordHistoryPolicy.from_dict(merged_data)
                self._policy_cache[company_uuid] = policy
                return policy
                
            except Exception as e:
                logger.error(f"Error loading policy for company {company_uuid}: {e}")
        
        # Return default policy and cache it
        self._policy_cache[company_uuid] = self.default_policy
        return self.default_policy
    
    def set_company_policy(self, company_uuid: str, policy: PasswordHistoryPolicy):
        """Set policy for a specific company"""
        if 'company_policies' not in self._config_data:
            self._config_data['company_policies'] = {}
        
        self._config_data['company_policies'][company_uuid] = policy.to_dict()
        self._policy_cache[company_uuid] = policy
        
        logger.info(f"Set custom policy for company: {company_uuid}")
    
    def update_default_policy(self, **kwargs):
        """Update default policy with new values"""
        policy_data = self.default_policy.to_dict()
        policy_data.update(kwargs)
        
        try:
            self.default_policy = PasswordHistoryPolicy.from_dict(policy_data)
            self._config_data['password_history_policy'] = policy_data
            
            # Clear cache to force reload
            self._policy_cache.clear()
            
            logger.info("Updated default password history policy")
            
        except Exception as e:
            logger.error(f"Error updating default policy: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # Try to get from policy first
        if hasattr(self.default_policy, key):
            return getattr(self.default_policy, key)
        
        # Fall back to general config
        return self._config_data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config_data[key] = value
    
    def get_company_config(self, company_uuid: str, key: str, default: Any = None) -> Any:
        """Get company-specific configuration value"""
        company_policies = self._config_data.get('company_policies', {})
        company_config = company_policies.get(company_uuid, {})
        
        if key in company_config:
            return company_config[key]
        
        # Fall back to default
        return self.get(key, default)
    
    def validate_policy(self, policy: PasswordHistoryPolicy) -> List[str]:
        """Validate a policy configuration"""
        errors = []
        
        # Validate max history bounds
        if policy.default_max_history < policy.minimum_max_history:
            errors.append("default_max_history cannot be less than minimum_max_history")
        
        if policy.default_max_history > policy.maximum_max_history:
            errors.append("default_max_history cannot be greater than maximum_max_history")
        
        if policy.minimum_max_history < 1:
            errors.append("minimum_max_history must be at least 1")
        
        if policy.maximum_max_history > 100:
            errors.append("maximum_max_history should not exceed 100 for performance reasons")
        
        # Validate cache settings
        if policy.cache_enabled:
            if policy.cache_ttl < 60:
                errors.append("cache_ttl should be at least 60 seconds")
            
            if policy.cache_max_size < 100:
                errors.append("cache_max_size should be at least 100")
        
        # Validate backup settings
        if policy.backup_enabled:
            if policy.backup_retention_count < 1:
                errors.append("backup_retention_count must be at least 1")
            
            if policy.auto_backup_interval < 3600:
                errors.append("auto_backup_interval should be at least 1 hour")
        
        # Validate audit settings
        if policy.audit_enabled:
            if policy.audit_retention_days < 7:
                errors.append("audit_retention_days should be at least 7 days")
        
        # Validate concurrency settings
        if policy.concurrency_max_retries < 1:
            errors.append("concurrency_max_retries must be at least 1")
        
        if policy.concurrency_retry_delay < 0.01:
            errors.append("concurrency_retry_delay must be at least 0.01 seconds")
        
        return errors
    
    def save_to_file(self, file_path: str = None) -> bool:
        """Save current configuration to file"""
        target_file = Path(file_path) if file_path else self.config_file
        
        if not target_file:
            logger.error("No file path specified for saving configuration")
            return False
        
        try:
            # Ensure directory exists
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare config data for saving
            config_to_save = self._config_data.copy()
            config_to_save['password_history_policy'] = self.default_policy.to_dict()
            
            with open(target_file, 'w') as f:
                json.dump(config_to_save, f, indent=2, sort_keys=True)
            
            logger.info(f"Configuration saved to {target_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to file: {e}")
            return False
    
    def reload_from_file(self) -> bool:
        """Reload configuration from file"""
        if not self.config_file or not self.config_file.exists():
            logger.warning("No configuration file to reload from")
            return False
        
        try:
            self._config_data.clear()
            self._policy_cache.clear()
            self._load_from_file()
            self._merge_config_with_policy()
            
            logger.info("Configuration reloaded from file")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            return False
    
    def get_effective_config(self, company_uuid: str = None) -> Dict[str, Any]:
        """Get the effective configuration for a company"""
        policy = self.get_policy(company_uuid)
        
        config = {
            'policy': policy.to_dict(),
            'company_uuid': company_uuid,
            'general_settings': {}
        }
        
        # Add general settings that aren't part of the policy
        general_keys = [
            'storage_encryption_key_rotation_days',
            'password_complexity_requirements',
            'notification_settings',
            'integration_settings'
        ]
        
        for key in general_keys:
            if company_uuid:
                value = self.get_company_config(company_uuid, key)
            else:
                value = self.get(key)
            
            if value is not None:
                config['general_settings'][key] = value
        
        return config
    
    def export_config(self) -> Dict[str, Any]:
        """Export full configuration for backup/migration"""
        return {
            'default_policy': self.default_policy.to_dict(),
            'company_policies': self._config_data.get('company_policies', {}),
            'general_settings': {
                k: v for k, v in self._config_data.items() 
                if k not in ['password_history_policy', 'company_policies']
            },
            'export_timestamp': str(datetime.now().isoformat())
        }
    
    def import_config(self, config_data: Dict[str, Any]) -> bool:
        """Import configuration from exported data"""
        try:
            # Validate the import data structure
            if 'default_policy' not in config_data:
                raise ValueError("Invalid config data: missing default_policy")
            
            # Import default policy
            self.default_policy = PasswordHistoryPolicy.from_dict(config_data['default_policy'])
            
            # Import company policies
            if 'company_policies' in config_data:
                self._config_data['company_policies'] = config_data['company_policies']
            
            # Import general settings
            if 'general_settings' in config_data:
                self._config_data.update(config_data['general_settings'])
            
            # Clear policy cache
            self._policy_cache.clear()
            
            logger.info("Configuration imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False