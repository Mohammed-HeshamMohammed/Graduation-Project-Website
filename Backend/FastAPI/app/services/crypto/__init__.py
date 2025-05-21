# app/services/crypto/__init__.py
"""
Cryptographic services for secure data handling.

This module provides encryption, decryption, and key management 
functionality with automatic key rotation and multiple cipher support.
"""

import time
from typing import Optional

from app.middleware.security import validate_input, rate_limit
from app.services.logging_service import security_log
from app.config import settings

from .constants import DEFAULT_CIPHER, LAYERED_ENCRYPTION, USE_CHACHA
from .constants import CIPHER_AES_GCM, CIPHER_CHACHA20_POLY1305, CIPHER_LAYERED
from .exceptions import CryptoException, DecryptionError, EncryptionError
from .key_management import get_current_key_version
from .utils import derive_key, extract_version
from .ciphers import (
    encrypt_aes_gcm, encrypt_chacha20_poly1305,
    decrypt_aes_gcm, decrypt_chacha20_poly1305,
    layered_encrypt, layered_decrypt, emergency_decrypt
)

__all__ = [
    'encrypt_data', 'decrypt_data',
    'encrypt_with_failsafe', 'decrypt_with_failsafe',
    'CryptoException'
]

@rate_limit
def encrypt_data(data: bytes, cipher_type: str = DEFAULT_CIPHER, client_ip: str = '0.0.0.0') -> bytes:
    """Encrypt data using selected cipher with proper key derivation and versioning"""
    try:
        # Validate input
        data = validate_input(data)
        
        # Get current key version for rotation
        version = get_current_key_version()
        
        # Derive a secure key from the configuration key with version
        key = derive_key(settings.ENCRYPTION_KEY, version)
        
        # Choose encryption method based on configuration and request
        if LAYERED_ENCRYPTION:
            encrypted_data = layered_encrypt(data, key, version)
        elif cipher_type.upper() == "CHACHA20" and USE_CHACHA:
            encrypted_data = encrypt_chacha20_poly1305(data, key, version)
        else:
            encrypted_data = encrypt_aes_gcm(data, key, version)
        
        # Log encryption event (without sensitive data)
        security_log(
            "ENCRYPTION", 
            f"Data encrypted with key version {version}, cipher: {cipher_type}, length: {len(data)} bytes",
            module="crypto"
        )
        
        return encrypted_data
    except Exception as e:
        security_log("ENCRYPTION_ERROR", f"Encryption error: {type(e).__name__}: {e}", module="crypto")
        raise

@rate_limit
def decrypt_data(encrypted_data: bytes, client_ip: str = '0.0.0.0') -> bytes:
    """Decrypt encrypted data with proper key derivation and versioning"""
    try:
        # Validate input
        encrypted_data = validate_input(encrypted_data)
        
        # Check if data is too short
        if len(encrypted_data) < 5:
            raise ValueError("Encrypted data is too short")
        
        # Extract version
        version, _ = extract_version(encrypted_data)
        
        # Derive the key with the specified version
        key = derive_key(settings.ENCRYPTION_KEY, version)
        
        # Determine encryption type and decrypt accordingly
        if encrypted_data[4:5] == CIPHER_LAYERED:
            # Layered encryption
            decrypted_data = layered_decrypt(encrypted_data[4:], key, version)
        elif encrypted_data[4:5] == CIPHER_AES_GCM:
            # AES-GCM
            decrypted_data = decrypt_aes_gcm(encrypted_data[4:], key, version)
        elif encrypted_data[4:5] == CIPHER_CHACHA20_POLY1305:
            # ChaCha20-Poly1305
            decrypted_data = decrypt_chacha20_poly1305(encrypted_data[4:], key, version)
        else:
            raise ValueError(f"Unknown cipher type: {encrypted_data[4:5].hex()}")
        
        # Log decryption success
        security_log(
            "DECRYPTION",
            f"Data decrypted successfully with key version {version}, length: {len(decrypted_data)} bytes",
            module="crypto"
        )
        
        return decrypted_data
    except Exception as e:
        security_log("DECRYPTION_ERROR", f"Decryption error: {type(e).__name__}: {e}", module="crypto")
        raise

@rate_limit
def encrypt_with_failsafe(data: bytes, cipher_type: str = DEFAULT_CIPHER, client_ip: str = '0.0.0.0') -> bytes:
    """Encrypt data with additional failsafe mechanisms"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return encrypt_data(data, cipher_type, client_ip)
        except Exception as e:
            security_log("FAILSAFE", f"Encryption failsafe: Attempt {attempt+1} failed: {str(e)}", module="crypto")
            if attempt == max_retries - 1:
                raise
            time.sleep(0.5)

@rate_limit
def decrypt_with_failsafe(data: bytes, client_ip: str = '0.0.0.0') -> bytes:
    """Decrypt data with additional failsafe mechanisms"""
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return decrypt_data(data, client_ip)
        except Exception as e:
            last_error = e
            security_log("FAILSAFE", f"Decryption failsafe: Attempt {attempt+1} failed: {str(e)}", module="crypto")
            if attempt == max_retries - 1:
                # If all attempts fail, try one last approach with different formats
                try:
                    return emergency_decrypt(data, client_ip)
                except Exception as emergency_error:
                    security_log("EMERGENCY_FAILED", f"Emergency decryption failed: {str(emergency_error)}", module="crypto")
                    raise last_error
            time.sleep(0.5)