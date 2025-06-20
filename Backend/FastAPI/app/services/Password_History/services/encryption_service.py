# File: Password_History/services/encryption_service.py
"""Encryption service for password history data"""

import logging
from typing import bytes
from app.services.crypto import (
    encrypt_data, 
    decrypt_data, 
    encrypt_with_failsafe, 
    decrypt_with_failsafe, 
    CryptoException
)
from ..exceptions.password_exceptions import EncryptionException

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for handling encryption/decryption of password history data"""
    
    def __init__(self, client_ip: str = '127.0.0.1'):
        self.client_ip = client_ip
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data with failsafe fallback"""
        try:
            # Try failsafe encryption first
            return encrypt_with_failsafe(data, client_ip=self.client_ip)
        except CryptoException as e:
            logger.warning(f"Failsafe encryption failed: {e}, trying standard encryption")
            try:
                return encrypt_data(data, client_ip=self.client_ip)
            except CryptoException as fallback_error:
                logger.error(f"All encryption methods failed: {fallback_error}")
                raise EncryptionException(f"Failed to encrypt data: {fallback_error}")
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data with failsafe fallback"""
        if not encrypted_data:
            raise EncryptionException("No data to decrypt")
        
        try:
            # Try failsafe decryption first
            return decrypt_with_failsafe(encrypted_data, client_ip=self.client_ip)
        except CryptoException as e:
            logger.warning(f"Failsafe decryption failed: {e}, trying standard decryption")
            try:
                return decrypt_data(encrypted_data, client_ip=self.client_ip)
            except CryptoException as fallback_error:
                logger.error(f"All decryption methods failed: {fallback_error}")
                raise EncryptionException(f"Failed to decrypt data: {fallback_error}")
