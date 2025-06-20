"""
Base storage class providing common functionality for encrypted data storage.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.services.crypto import encrypt_with_failsafe, decrypt_with_failsafe, encrypt_data, decrypt_data, CryptoException
from app.config import settings

logger = logging.getLogger(__name__)


class BaseStorage:
    """Base class for encrypted storage operations."""
    
    def __init__(self):
        """Initialize storage with data directory from settings."""
        self.data_dir = Path(settings.DATA_DIR)
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Define sensitive fields that should NEVER be returned to frontend
        self.SENSITIVE_FIELDS = {
            'password', 'password_hash', 'hashed_password', 'salt', 'password_salt',
            'api_keys', 'tokens', 'access_token', 'refresh_token', 'session_token',
            'private_keys', 'secret_key', 'encryption_key', 'signing_key',
            'two_factor_secret', '2fa_secret', 'backup_codes', 'recovery_codes',
            'security_questions', 'security_answers', 'pin', 'pin_hash',
            'oauth_tokens', 'social_tokens', 'internal_id', 'system_id',
            'admin_notes', 'internal_notes', 'flags', 'audit_log',
            'payment_info', 'credit_card', 'bank_account', 'ssn', 'tax_id',
            'personal_documents', 'id_verification', 'kyc_data', 'password_history'
        }
    
    def load_encrypted_data(self, file_path: Path, data_type: str) -> Dict[str, Any]:
        """
        Load and decrypt data from file.
        
        Args:
            file_path: Path to the encrypted file
            data_type: Type of data being loaded (for logging)
            
        Returns:
            Dictionary containing the decrypted data
        """
        if not os.path.exists(file_path):
            logger.info(f"{data_type.title()} file does not exist at {file_path}, creating new store")
            return {}
        
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    logger.info(f"{data_type.title()} file exists but is empty")
                    return {}
                
                # Use failsafe decryption for better reliability
                try:
                    decrypted_data = decrypt_with_failsafe(encrypted_data, client_ip='127.0.0.1')
                except CryptoException as e:
                    logger.error(f"Failsafe decryption failed for {data_type}: {e}")
                    try:
                        decrypted_data = decrypt_data(encrypted_data, client_ip='127.0.0.1')
                    except CryptoException as fallback_error:
                        logger.error(f"All decryption methods failed for {data_type}: {fallback_error}")
                        logger.warning(f"Unable to decrypt {data_type}, starting fresh")
                        return {}
                
                data = json.loads(decrypted_data.decode('utf-8'))
                logger.info(f"Loaded {data_type} for {len(data)} item(s)")
                return data
                
        except FileNotFoundError:
            logger.warning(f"{data_type.title()} file not found at {file_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding {data_type} JSON: {e}")
            if data_type == "users":
                self._create_backup_and_reset(file_path)
            return {}
        except Exception as e:
            logger.error(f"Error loading {data_type}: {type(e).__name__}: {e}")
            return {}
    
    def save_encrypted_data(self, data: Dict[str, Any], file_path: Path, data_type: str) -> bool:
        """
        Encrypt and save data to file.
        
        Args:
            data: Dictionary to encrypt and save
            file_path: Path where to save the encrypted file
            data_type: Type of data being saved (for logging)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert data to JSON and then to bytes
            data_json = json.dumps(data, indent=2, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # Use failsafe encryption for better reliability
            try:
                encrypted_data = encrypt_with_failsafe(data_bytes, client_ip='127.0.0.1')
            except CryptoException as e:
                logger.error(f"Failsafe encryption failed for {data_type}: {e}")
                try:
                    encrypted_data = encrypt_data(data_bytes, client_ip='127.0.0.1')
                except CryptoException as fallback_error:
                    logger.error(f"All encryption methods failed for {data_type}: {fallback_error}")
                    return False
            
            # Create backup of existing file before overwriting
            if file_path.exists():
                backup_path = file_path.with_suffix('.bak')
                try:
                    backup_path.write_bytes(file_path.read_bytes())
                    logger.debug(f"Created backup at {backup_path}")
                except Exception as backup_error:
                    logger.warning(f"Could not create backup for {data_type}: {backup_error}")
            
            # Write to temporary file first, then move to final location
            temp_path = file_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Atomic move to final location
                temp_path.replace(file_path)
                
                logger.info(f"Saved {data_type} data successfully")
                return True
                
            except Exception as write_error:
                logger.error(f"Error writing encrypted {data_type} data: {write_error}")
                # Clean up temp file if it exists
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
                return False
                
        except Exception as e:
            logger.error(f"Error saving {data_type} data: {type(e).__name__}: {e}")
            return False
    
    def _create_backup_and_reset(self, file_path: Path):
        """Create a backup of corrupted data and reset to empty state."""
        try:
            if file_path.exists():
                timestamp = int(time.time())
                corrupted_backup = file_path.with_name(f"corrupted_{file_path.stem}_{timestamp}.bak")
                file_path.rename(corrupted_backup)
                logger.warning(f"Corrupted data backed up to {corrupted_backup}")
        except Exception as e:
            logger.error(f"Failed to backup corrupted data: {e}")
    
    def validate_input(self, value: Any, expected_type: type, field_name: str) -> bool:
        """
        Validate input parameters.
        
        Args:
            value: Value to validate
            expected_type: Expected type of the value
            field_name: Name of the field for logging
            
        Returns:
            True if valid, False otherwise
        """
        if not value or not isinstance(value, expected_type):
            logger.warning(f"Invalid {field_name} provided: {type(value).__name__}")
            return False
        return True
    
    def sanitize_email(self, email: str) -> Optional[str]:
        """
        Sanitize and validate email address.
        
        Args:
            email: Email address to sanitize
            
        Returns:
            Sanitized email or None if invalid
        """
        if not self.validate_input(email, str, "email"):
            return None
        
        sanitized = email.lower().strip()
        if not sanitized:
            logger.warning("Empty email after sanitization")
            return None
        
        return sanitized