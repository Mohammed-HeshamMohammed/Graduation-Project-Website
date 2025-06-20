# ciphers/emergency.py
"""
Emergency decryption functionality for last resort data recovery.
"""

from typing import Optional
from Crypto.Cipher import AES
from .types import CipherType, VERSION_SIZE, TYPE_SIZE, NONCE_SIZE, TAG_SIZE, MIN_ENCRYPTED_SIZE, unpack_version
from .utils import split_encrypted_data, validate_encrypted_data
from .registry import cipher_registry
from ..exceptions import DecryptionError
from ...logging_service import security_log
from ..utils import derive_key


def emergency_decrypt(data: bytes, encryption_key: str, client_ip: str = '0.0.0.0', 
                     allow_emergency: bool = True) -> bytes:
    """
    Last resort decryption attempt with multiple formats and legacy handling.
    
    This function attempts to decrypt data using various strategies:
    1. Smart decrypt with version 1 (modern format)
    2. Legacy AES-GCM format (no version prefix)
    3. Try different versions with all registered cipher types
    
    Args:
        data: Encrypted data bytes
        encryption_key: Base encryption key
        client_ip: Client IP for logging purposes
        allow_emergency: Whether emergency decryption is allowed
        
    Returns:
        Decrypted data bytes
        
    Raises:
        DecryptionError: If all decryption attempts fail
    """
    if not allow_emergency:
        security_log("EMERGENCY_BLOCKED", "Emergency decryption is disabled", module="crypto.ciphers.emergency")
        raise DecryptionError("Emergency decryption is disabled")
    
    security_log("EMERGENCY", f"Attempting emergency decryption from IP: {client_ip}", module="crypto.ciphers.emergency")
    
    # Try with default version 1
    key = derive_key(encryption_key, 1)
    
    # Strategy 1: Try modern format first with smart decrypt
    try:
        security_log("EMERGENCY_ATTEMPT", "Trying smart decrypt with version 1", module="crypto.ciphers.emergency")
        result = _smart_decrypt_attempt(data, key, 1)
        security_log("EMERGENCY_SUCCESS", "Smart decrypt with version 1 worked", module="crypto.ciphers.emergency")
        return result
    except Exception as e:
        security_log("EMERGENCY_ATTEMPT", f"Smart decrypt failed: {str(e)}", module="crypto.ciphers.emergency")
    
    # Strategy 2: Try legacy format (no version prefix)
    try:
        security_log("EMERGENCY_ATTEMPT", "Trying legacy AES-GCM format", module="crypto.ciphers.emergency")
        result = _legacy_aes_gcm_decrypt(data, key)
        security_log("EMERGENCY_SUCCESS", "Legacy AES-GCM format worked", module="crypto.ciphers.emergency")
        return result
    except Exception as e:
        security_log("EMERGENCY_ATTEMPT", f"Legacy AES-GCM failed: {str(e)}", module="crypto.ciphers.emergency")
    
    # Strategy 3: Try with different versions and cipher types
    try:
        result = _version_brute_force_decrypt(data, encryption_key)
        security_log("EMERGENCY_SUCCESS", "Version brute force worked", module="crypto.ciphers.emergency")
        return result
    except Exception as e:
        security_log("EMERGENCY_ATTEMPT", f"Version brute force failed: {str(e)}", module="crypto.ciphers.emergency")
    
    security_log("EMERGENCY_FAILED", "All emergency decryption attempts failed", module="crypto.ciphers.emergency")
    raise DecryptionError("Emergency decryption failed with all attempts")


def _smart_decrypt_attempt(data: bytes, key: bytes, version: int) -> bytes:
    """Attempt smart decrypt with automatic cipher type detection."""
    from .registry import cipher_registry
    
    cipher_type = cipher_registry.detect_cipher_type(data)
    cipher = cipher_registry.get_cipher(cipher_type)
    security_log("DECRYPT_ATTEMPT", f"Using cipher: {cipher_type.name}, version: {version}", 
                 module="crypto.ciphers.emergency")
    return cipher.decrypt(data, key, version)


def _legacy_aes_gcm_decrypt(data: bytes, key: bytes) -> bytes:
    """Attempt legacy AES-GCM decryption without version prefix."""
    legacy_min_size = NONCE_SIZE + TAG_SIZE
    if len(data) < legacy_min_size:
        raise DecryptionError(f"Legacy encrypted data too short: {len(data)} < {legacy_min_size}")
    
    # Legacy format: nonce + tag + ciphertext (no version, no cipher type)
    _, nonce, tag, ciphertext = split_encrypted_data(data, has_version=False)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def _version_brute_force_decrypt(data: bytes, encryption_key: str) -> bytes:
    """Try different versions and cipher types to decrypt data."""
    if len(data) < MIN_ENCRYPTED_SIZE:
        raise DecryptionError(f"Data too short for version brute force: {len(data)} < {MIN_ENCRYPTED_SIZE}")
    
    try:
        version = unpack_version(data)
        security_log("EMERGENCY_ATTEMPT", f"Trying version {version} with format guessing", 
                     module="crypto.ciphers.emergency")
        
        if not (0 < version < 100):  # Reasonable version range check
            raise DecryptionError(f"Version {version} outside reasonable range")
        
        key = derive_key(encryption_key, version)
        
        # Try all registered cipher types
        for cipher_type in CipherType:
            try:
                if cipher_type in cipher_registry._ciphers:
                    security_log("EMERGENCY_ATTEMPT", 
                                f"Trying {cipher_type.name} with version {version}", 
                                module="crypto.ciphers.emergency")
                    cipher = cipher_registry.get_cipher(cipher_type)
                    result = cipher.decrypt(data, key, version)
                    security_log("EMERGENCY_SUCCESS", 
                                f"{cipher_type.name} with version {version} worked", 
                                module="crypto.ciphers.emergency")
                    return result
            except Exception as e:
                security_log("EMERGENCY_ATTEMPT", 
                            f"{cipher_type.name} v{version} failed: {str(e)}", 
                            module="crypto.ciphers.emergency")
                continue
        
        raise DecryptionError(f"No cipher type worked for version {version}")
        
    except Exception as e:
        security_log("EMERGENCY_ATTEMPT", f"Version extraction failed: {str(e)}", 
                     module="crypto.ciphers.emergency")
        raise DecryptionError(f"Version brute force failed: {str(e)}")


def emergency_decrypt_with_fallback(data: bytes, encryption_key: str, 
                                   fallback_keys: Optional[list] = None,
                                   client_ip: str = '0.0.0.0',
                                   allow_emergency: bool = True) -> bytes:
    """
    Emergency decrypt with additional fallback keys.
    
    Args:
        data: Encrypted data bytes
        encryption_key: Primary encryption key
        fallback_keys: Optional list of fallback keys to try
        client_ip: Client IP for logging
        allow_emergency: Whether emergency decryption is allowed
        
    Returns:
        Decrypted data bytes
        
    Raises:
        DecryptionError: If all attempts fail
    """
    # Try primary key first
    try:
        return emergency_decrypt(data, encryption_key, client_ip, allow_emergency)
    except DecryptionError as e:
        security_log("EMERGENCY_FALLBACK", f"Primary key failed: {str(e)}", 
                     module="crypto.ciphers.emergency")
    
    # Try fallback keys if provided
    if fallback_keys:
        for i, fallback_key in enumerate(fallback_keys):
            try:
                security_log("EMERGENCY_FALLBACK", f"Trying fallback key {i+1}/{len(fallback_keys)}", 
                           module="crypto.ciphers.emergency")
                return emergency_decrypt(data, fallback_key, client_ip, allow_emergency)
            except DecryptionError as e:
                security_log("EMERGENCY_FALLBACK", f"Fallback key {i+1} failed: {str(e)}", 
                           module="crypto.ciphers.emergency")
                continue
    
    security_log("EMERGENCY_FAILED", "All emergency decryption attempts including fallbacks failed", 
                 module="crypto.ciphers.emergency")
    raise DecryptionError("Emergency decryption failed with all attempts including fallbacks")


def validate_emergency_conditions(data: bytes, allow_emergency: bool = True) -> bool:
    """
    Validate if emergency decryption should be attempted.
    
    Args:
        data: Data to validate
        allow_emergency: Whether emergency decryption is allowed
        
    Returns:
        True if emergency decryption should be attempted
        
    Raises:
        DecryptionError: If conditions are not met
    """
    if not allow_emergency:
        raise DecryptionError("Emergency decryption is disabled")
    
    if not data:
        raise DecryptionError("No data provided for emergency decryption")
    
    if len(data) < 16:  # Minimum reasonable size
        raise DecryptionError(f"Data too short for any decryption attempt: {len(data)} bytes")
    
    return True


def get_emergency_decrypt_info(data: bytes) -> dict:
    """
    Get information about encrypted data for emergency decryption diagnostics.
    
    Args:
        data: Encrypted data bytes
        
    Returns:
        Dictionary with diagnostic information
    """
    info = {
        "data_length": len(data),
        "has_version": False,
        "version": None,
        "cipher_type": None,
        "format": "unknown"
    }
    
    try:
        # Check if it looks like modern format
        if len(data) >= MIN_ENCRYPTED_SIZE:
            try:
                version = unpack_version(data)
                if 0 < version < 100:  # Reasonable version range
                    info["has_version"] = True
                    info["version"] = version
                    info["format"] = "modern"
                    
                    # Try to detect cipher type
                    type_byte = data[VERSION_SIZE:VERSION_SIZE + TYPE_SIZE]
                    for cipher_type in CipherType:
                        if cipher_type.value == type_byte:
                            info["cipher_type"] = cipher_type.name
                            break
            except:
                pass
        
        # Check if it looks like legacy format
        legacy_min_size = NONCE_SIZE + TAG_SIZE
        if len(data) >= legacy_min_size and not info["has_version"]:
            info["format"] = "legacy"
            
    except Exception as e:
        info["error"] = str(e)
    
    return info