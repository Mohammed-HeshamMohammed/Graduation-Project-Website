# File: Password_History/services/history_service.py
"""Core password history business logic service"""

import logging
import uuid
import time
from typing import Dict, List, Optional
from app.services.storage import UserStorage
from .storage_service import StorageService
from .encryption_service import EncryptionService
from .audit_service import AuditService
from ..models.password_history import PasswordHistoryModel, PasswordHistoryEntry
from ..exceptions.password_exceptions import (
    PasswordReusedException, 
    ValidationException
)
from ..utils.validators import PasswordHistoryValidator

logger = logging.getLogger(__name__)

class PasswordHistoryService:
    """Core service for password history operations"""
    
    def __init__(self, 
                 user_storage: UserStorage = None,
                 storage_service: StorageService = None,
                 validator: PasswordHistoryValidator = None,
                 audit_service: AuditService = None):
        self.user_storage = user_storage or UserStorage()
        self.storage_service = storage_service or StorageService()
        self.validator = validator or PasswordHistoryValidator()
        self.audit_service = audit_service
        self.model = self.storage_service.load_password_history()
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID for audit logging"""
        return f"pwd_hist_{int(time.time() * 1000)}_{str(uuid.uuid4())[:8]}"
    
    def _log_operation_start(self, operation_type: str, user_uuid: str = None, 
                           company_uuid: str = None, requesting_user_uuid: str = None,
                           ip_address: str = None, user_agent: str = None,
                           metadata: Dict = None) -> str:
        """Log the start of an operation and return operation ID"""
        operation_id = self._generate_operation_id()
        
        if self.audit_service:
            self.audit_service.log_operation_start(
                operation_id=operation_id,
                operation_type=operation_type,
                user_uuid=user_uuid,
                company_uuid=company_uuid,
                requesting_user_uuid=requesting_user_uuid,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata
            )
        
        return operation_id
    
    def _log_operation_success(self, operation_id: str, metadata: Dict = None):
        """Log successful operation completion"""
        if self.audit_service:
            self.audit_service.log_operation_success(operation_id, metadata)
    
    def _log_operation_error(self, operation_id: str, error_message: str, metadata: Dict = None):
        """Log failed operation completion"""
        if self.audit_service:
            self.audit_service.log_operation_error(operation_id, error_message, metadata)
    
    def _log_security_event(self, event_type: str, user_uuid: str = None, 
                          company_uuid: str = None, severity: str = 'medium',
                          details: Dict = None):
        """Log security-related events"""
        if self.audit_service:
            self.audit_service.log_security_event(
                event_type=event_type,
                user_uuid=user_uuid,
                company_uuid=company_uuid,
                severity=severity,
                details=details
            )
    
    def add_password_to_history(self, 
                              user_uuid: str, 
                              company_uuid: str, 
                              password_hash: str, 
                              max_history: int = 5,
                              requesting_user_uuid: str = None,
                              ip_address: str = None,
                              user_agent: str = None) -> bool:
        """Add password to user's history"""
        operation_id = self._log_operation_start(
            operation_type='add_password_to_history',
            user_uuid=user_uuid,
            company_uuid=company_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                'max_history': max_history,
                'password_hash_length': len(password_hash) if password_hash else 0
            }
        )
        
        try:
            # Validate inputs
            self.validator.validate_uuid(user_uuid, "user_uuid")
            self.validator.validate_uuid(company_uuid, "company_uuid")
            self.validator.validate_password_hash(password_hash)
            self.validator.validate_max_history(max_history)
            
            # Add to model
            added = self.model.add_entry(user_uuid, company_uuid, password_hash, max_history)
            
            if not added:
                logger.debug(f"Password already matches most recent for user: {user_uuid}")
                self._log_operation_success(operation_id, {'result': 'duplicate_password_skipped'})
                return True
            
            # Save to storage
            success = self.storage_service.save_password_history(self.model)
            
            if success:
                logger.info(f"Added password to history for user: {user_uuid}")
                self._log_operation_success(operation_id, {
                    'result': 'password_added_to_history',
                    'current_history_count': self.model.get_user_history_count(user_uuid)
                })
            else:
                logger.error(f"Failed to save password history for user: {user_uuid}")
                self._log_operation_error(operation_id, "Failed to save password history to storage")
            
            return success
            
        except ValidationException as e:
            logger.error(f"Validation error adding password to history: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error adding password to history: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return False
    
    def check_password_reuse(self, user_uuid: str, password_hash: str,
                           requesting_user_uuid: str = None,
                           ip_address: str = None,
                           user_agent: str = None) -> bool:
        """Check if password was used before"""
        operation_id = self._log_operation_start(
            operation_type='check_password_reuse',
            user_uuid=user_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                'password_hash_length': len(password_hash) if password_hash else 0
            }
        )
        
        try:
            self.validator.validate_uuid(user_uuid, "user_uuid")
            self.validator.validate_password_hash(password_hash)
            
            is_reused = self.model.check_password_exists(user_uuid, password_hash)
            
            if is_reused:
                logger.info(f"Password found in history for user: {user_uuid}")
                self._log_security_event(
                    event_type='password_reuse_attempt',
                    user_uuid=user_uuid,
                    severity='high',
                    details={
                        'requesting_user': requesting_user_uuid,
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    }
                )
                self._log_operation_success(operation_id, {'result': 'password_found_in_history'})
            else:
                logger.debug(f"Password not found in history for user: {user_uuid}")
                self._log_operation_success(operation_id, {'result': 'password_not_in_history'})
            
            return is_reused
            
        except ValidationException as e:
            logger.error(f"Validation error checking password history: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error checking password history: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return False
    
    def update_user_password(self, 
                           user_uuid: str, 
                           company_uuid: str, 
                           new_password_hash: str,
                           requesting_user_uuid: str = None,
                           ip_address: str = None,
                           user_agent: str = None) -> bool:
        """Update user password and add to history"""
        operation_id = self._log_operation_start(
            operation_type='update_user_password',
            user_uuid=user_uuid,
            company_uuid=company_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                'password_hash_length': len(new_password_hash) if new_password_hash else 0
            }
        )
        
        try:
            # Validate inputs
            self.validator.validate_uuid(user_uuid, "user_uuid")
            self.validator.validate_uuid(company_uuid, "company_uuid")
            self.validator.validate_password_hash(new_password_hash)
            
            # Find user by UUID
            user_data = self.user_storage.get_user_by_uuid(user_uuid)
            if not user_data:
                logger.error(f"User not found with UUID: {user_uuid}")
                self._log_security_event(
                    event_type='password_update_invalid_user',
                    user_uuid=user_uuid,
                    company_uuid=company_uuid,
                    severity='high',
                    details={
                        'requesting_user': requesting_user_uuid,
                        'ip_address': ip_address,
                        'reason': 'user_not_found'
                    }
                )
                self._log_operation_error(operation_id, "User not found")
                return False
            
            # Verify user belongs to the company
            if user_data.get('company_uuid') != company_uuid:
                logger.error(f"User {user_uuid} does not belong to company {company_uuid}")
                self._log_security_event(
                    event_type='password_update_company_mismatch',
                    user_uuid=user_uuid,
                    company_uuid=company_uuid,
                    severity='high',
                    details={
                        'requesting_user': requesting_user_uuid,
                        'ip_address': ip_address,
                        'user_company': user_data.get('company_uuid'),
                        'requested_company': company_uuid
                    }
                )
                self._log_operation_error(operation_id, "User does not belong to specified company")
                return False
            
            # Check if password was used before
            if self.check_password_reuse(user_uuid, new_password_hash, requesting_user_uuid, ip_address, user_agent):
                logger.warning(f"Password was used before for user: {user_uuid}")
                self._log_operation_error(operation_id, "Password reuse detected")
                raise PasswordReusedException("Password has been used before")
            
            # Update user password in storage
            user_data['password'] = new_password_hash
            success = self.user_storage.update_user(user_data)
            
            if not success:
                logger.error(f"Failed to update user password in storage for: {user_uuid}")
                self._log_operation_error(operation_id, "Failed to update user password in storage")
                return False
            
            # Add to password history
            history_success = self.add_password_to_history(
                user_uuid, company_uuid, new_password_hash,
                requesting_user_uuid=requesting_user_uuid,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if not history_success:
                logger.warning(f"Password updated but failed to add to history for: {user_uuid}")
                # Don't fail the whole operation if history fails
            
            logger.info(f"Successfully updated password for user: {user_uuid}")
            self._log_operation_success(operation_id, {
                'result': 'password_updated_successfully',
                'history_updated': history_success
            })
            
            # Log successful password change as security event
            self._log_security_event(
                event_type='password_changed',
                user_uuid=user_uuid,
                company_uuid=company_uuid,
                severity='low',
                details={
                    'requesting_user': requesting_user_uuid,
                    'ip_address': ip_address,
                    'history_updated': history_success
                }
            )
            
            return True
            
        except PasswordReusedException:
            raise
        except ValidationException as e:
            logger.error(f"Validation error updating user password: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error updating user password: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return False
    
    def get_company_password_histories(self, company_uuid: str,
                                     requesting_user_uuid: str = None,
                                     ip_address: str = None,
                                     user_agent: str = None) -> Dict[str, List[PasswordHistoryEntry]]:
        """Get all password histories for users in a company"""
        operation_id = self._log_operation_start(
            operation_type='get_company_password_histories',
            company_uuid=company_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            self.validator.validate_uuid(company_uuid, "company_uuid")
            histories = self.model.get_company_histories(company_uuid)
            
            self._log_operation_success(operation_id, {
                'result': 'company_histories_retrieved',
                'user_count': len(histories),
                'total_entries': sum(len(entries) for entries in histories.values())
            })
            
            return histories
            
        except ValidationException as e:
            logger.error(f"Validation error getting company password histories: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error getting company password histories: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return {}
    
    def get_user_history_count(self, user_uuid: str,
                             requesting_user_uuid: str = None,
                             ip_address: str = None,
                             user_agent: str = None) -> int:
        """Get the number of passwords in history for a user"""
        operation_id = self._log_operation_start(
            operation_type='get_user_history_count',
            user_uuid=user_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            self.validator.validate_uuid(user_uuid, "user_uuid")
            count = self.model.get_user_history_count(user_uuid)
            
            self._log_operation_success(operation_id, {
                'result': 'history_count_retrieved',
                'count': count
            })
            
            return count
            
        except ValidationException as e:
            logger.error(f"Validation error getting password history count: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return 0
        except Exception as e:
            logger.error(f"Error getting password history count: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return 0
    
    def clear_user_history(self, user_uuid: str, company_uuid: str,
                          requesting_user_uuid: str = None,
                          ip_address: str = None,
                          user_agent: str = None) -> bool:
        """Clear password history for a specific user (company admin only)"""
        operation_id = self._log_operation_start(
            operation_type='clear_user_history',
            user_uuid=user_uuid,
            company_uuid=company_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            self.validator.validate_uuid(user_uuid, "user_uuid")
            self.validator.validate_uuid(company_uuid, "company_uuid")
            
            # Get count before clearing for audit
            history_count = self.model.get_user_history_count(user_uuid)
            
            # Verify user belongs to the company
            user_data = self.user_storage.get_user_by_uuid(user_uuid)
            if not user_data or user_data.get('company_uuid') != company_uuid:
                logger.error(f"User {user_uuid} does not belong to company {company_uuid}")
                self._log_security_event(
                    event_type='clear_history_unauthorized_attempt',
                    user_uuid=user_uuid,
                    company_uuid=company_uuid,
                    severity='high',
                    details={
                        'requesting_user': requesting_user_uuid,
                        'ip_address': ip_address,
                        'reason': 'user_company_mismatch'
                    }
                )
                self._log_operation_error(operation_id, "User does not belong to specified company")
                return False
            
            self.model.clear_user_history(user_uuid)
            success = self.storage_service.save_password_history(self.model)
            
            if success:
                logger.info(f"Cleared password history for user: {user_uuid}")
                self._log_operation_success(operation_id, {
                    'result': 'history_cleared',
                    'entries_removed': history_count
                })
                
                # Log as security event
                self._log_security_event(
                    event_type='password_history_cleared',
                    user_uuid=user_uuid,
                    company_uuid=company_uuid,
                    severity='medium',
                    details={
                        'requesting_user': requesting_user_uuid,
                        'ip_address': ip_address,
                        'entries_removed': history_count
                    }
                )
            else:
                logger.error(f"Failed to save after clearing password history for user: {user_uuid}")
                self._log_operation_error(operation_id, "Failed to save after clearing history")
            
            return success
                
        except ValidationException as e:
            logger.error(f"Validation error clearing password history: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error clearing password history: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return False
    
    def cleanup_orphaned_histories(self,
                                 requesting_user_uuid: str = None,
                                 ip_address: str = None,
                                 user_agent: str = None) -> int:
        """Remove password histories for users that no longer exist"""
        operation_id = self._log_operation_start(
            operation_type='cleanup_orphaned_histories',
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            # Get all current user UUIDs from storage
            all_users = self.user_storage.get_all_users()
            current_uuids = set()
            
            for user_data in all_users.values():
                if isinstance(user_data, dict) and 'uuid' in user_data:
                    current_uuids.add(user_data['uuid'])
            
            # Clean up orphaned histories
            orphaned_count = self.model.cleanup_orphaned_histories(current_uuids)
            
            if orphaned_count > 0:
                success = self.storage_service.save_password_history(self.model)
                if success:
                    logger.info(f"Cleaned up {orphaned_count} orphaned password histories")
                    self._log_operation_success(operation_id, {
                        'result': 'orphaned_histories_cleaned',
                        'orphaned_count': orphaned_count,
                        'current_user_count': len(current_uuids)
                    })
                    
                    # Log as security event
                    self._log_security_event(
                        event_type='orphaned_histories_cleanup',
                        severity='low',
                        details={
                            'requesting_user': requesting_user_uuid,
                            'ip_address': ip_address,
                            'orphaned_count': orphaned_count
                        }
                    )
                else:
                    logger.error("Failed to save after cleaning up orphaned password histories")
                    self._log_operation_error(operation_id, "Failed to save after cleanup")
                    return 0
            else:
                logger.info("No orphaned password histories found")
                self._log_operation_success(operation_id, {
                    'result': 'no_orphaned_histories_found',
                    'current_user_count': len(current_uuids)
                })
            
            return orphaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up orphaned password histories: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return 0
    
    def get_statistics(self, company_uuid: str = None,
                      requesting_user_uuid: str = None,
                      ip_address: str = None,
                      user_agent: str = None) -> Dict:
        """Get statistics about password histories"""
        operation_id = self._log_operation_start(
            operation_type='get_statistics',
            company_uuid=company_uuid,
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            stats = self.model.get_statistics()
            
            # If company_uuid is provided, filter stats for that company
            if company_uuid:
                self.validator.validate_uuid(company_uuid, "company_uuid")
                company_histories = self.model.get_company_histories(company_uuid)
                
                # Calculate company-specific stats
                total_users = len(company_histories)
                total_passwords = sum(len(entries) for entries in company_histories.values())
                
                stats = {
                    'company_uuid': company_uuid,
                    'total_users_with_history': total_users,
                    'total_passwords_stored': total_passwords,
                    'average_passwords_per_user': round(total_passwords / total_users, 2) if total_users > 0 else 0,
                    'users_by_history_count': {}
                }
                
                # Count users by number of passwords in history for this company
                for entries in company_histories.values():
                    count = len(entries)
                    stats['users_by_history_count'][count] = stats['users_by_history_count'].get(count, 0) + 1
            
            self._log_operation_success(operation_id, {
                'result': 'statistics_retrieved',
                'company_specific': company_uuid is not None,
                'total_users': stats.get('total_users_with_history', 0)
            })
            
            return stats
            
        except ValidationException as e:
            logger.error(f"Validation error getting password history stats: {e}")
            self._log_operation_error(operation_id, f"Validation error: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Error getting password history stats: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return {}
    
    def create_backup(self, backup_path: str = None,
                     requesting_user_uuid: str = None,
                     ip_address: str = None,
                     user_agent: str = None) -> bool:
        """Create a backup of password history data"""
        operation_id = self._log_operation_start(
            operation_type='create_backup',
            requesting_user_uuid=requesting_user_uuid,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={'backup_path': backup_path}
        )
        
        try:
            success = self.storage_service.create_manual_backup(backup_path)
            
            if success:
                self._log_operation_success(operation_id, {
                    'result': 'backup_created_successfully',
                    'backup_path': backup_path
                })
                
                # Log as security event
                self._log_security_event(
                    event_type='password_history_backup_created',
                    severity='low',
                    details={
                        'requesting_user': requesting_user_uuid,
                        'ip_address': ip_address,
                        'backup_path': backup_path
                    }
                )
            else:
                self._log_operation_error(operation_id, "Failed to create backup")
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating backup: {type(e).__name__}: {e}")
            self._log_operation_error(operation_id, f"Unexpected error: {type(e).__name__}: {str(e)}")
            return False