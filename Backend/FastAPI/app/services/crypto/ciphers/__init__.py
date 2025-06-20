# ciphers/__init__.py
"""
Modular cipher implementations for secure encryption/decryption.

This module provides a clean API for various cipher implementations with automatic
cipher type detection, version management, and emergency decryption capabilities.
"""

from .types import CipherType
from .base import CipherInterface
from .registry import CipherRegistry, cipher_registry
from .emergency import emergency_decrypt, emergency_decrypt_with_fallback, get_emergency_decrypt_info

# Import all cipher implementations
from .aes_gcm import AESGCMCipher
from .chacha20 import ChaCha20Poly1305Cipher
from .xchacha20 import XChaCha20Poly1305Cipher
from .aes_siv import AESSIVCipher
from .camellia import CamelliaGCMCipher
from .layered import LayeredCipher

# Initialize the global registry with all available ciphers
def _initialize_registry():
    """Initialize the global cipher registry with all available ciphers."""
    from ...logging_service import get_module_logger
    
    logger = get_module_logger("crypto.ciphers", log_to_file=True)
    
    # Register core ciphers
    cipher_registry.register(AESGCMCipher())
    cipher_registry.register(ChaCha20Poly1305Cipher())
    cipher_registry.register(XChaCha20Poly1305Cipher())
    cipher_registry.register(AESSIVCipher())
    cipher_registry.register(LayeredCipher())
    
    # Register optional ciphers if available
    try:
        cipher_registry.register(CamelliaGCMCipher())
    except Exception as e:
        logger.warning(f"Camellia cipher not available: {e}")

# Initialize on import
_initialize_registry()

# Public API functions
def encrypt_aes_gcm(data: bytes, key: bytes, version: int) -> bytes:
    """Encrypt data using AES-256-GCM"""
    cipher = cipher_registry.get_cipher(CipherType.AES_GCM)
    return cipher.encrypt(data, key, version)

def encrypt_chacha20_poly1305(data: bytes, key: bytes, version: int) -> bytes:
    """Encrypt data using ChaCha20-Poly1305"""
    cipher = cipher_registry.get_cipher(CipherType.CHACHA20_POLY1305)
    return cipher.encrypt(data, key, version)

def encrypt_xchacha20_poly1305(data: bytes, key: bytes, version: int) -> bytes:
    """Encrypt data using XChaCha20-Poly1305 (recommended for real-time)"""
    cipher = cipher_registry.get_cipher(CipherType.XCHACHA20_POLY1305)
    return cipher.encrypt(data, key, version)

def encrypt_aes_siv(data: bytes, key: bytes, version: int) -> bytes:
    """Encrypt data using AES-SIV (deterministic, nonce-reuse resistant)"""
    cipher = cipher_registry.get_cipher(CipherType.AES_SIV)
    return cipher.encrypt(data, key, version)

def layered_encrypt(data: bytes, key: bytes, version: int) -> bytes:
    """Apply multiple layers of encryption for added security"""
    cipher = cipher_registry.get_cipher(CipherType.LAYERED)
    return cipher.encrypt(data, key, version)

def decrypt_aes_gcm(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt AES-256-GCM encrypted data"""
    cipher = cipher_registry.get_cipher(CipherType.AES_GCM)
    return cipher.decrypt(encrypted_data, key, version)

def decrypt_chacha20_poly1305(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt ChaCha20-Poly1305 encrypted data"""
    cipher = cipher_registry.get_cipher(CipherType.CHACHA20_POLY1305)
    return cipher.decrypt(encrypted_data, key, version)

def decrypt_xchacha20_poly1305(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt XChaCha20-Poly1305 encrypted data"""
    cipher = cipher_registry.get_cipher(CipherType.XCHACHA20_POLY1305)
    return cipher.decrypt(encrypted_data, key, version)

def decrypt_aes_siv(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt AES-SIV encrypted data"""
    cipher = cipher_registry.get_cipher(CipherType.AES_SIV)
    return cipher.decrypt(encrypted_data, key, version)

def layered_decrypt(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt multiple layers of encryption"""
    cipher = cipher_registry.get_cipher(CipherType.LAYERED)
    return cipher.decrypt(encrypted_data, key, version)

def smart_encrypt(data: bytes, key: bytes, version: int, use_case: str = "general") -> bytes:
    """Encrypt with recommended cipher based on use case"""
    from ...logging_service import security_log
    
    cipher_type = cipher_registry.get_recommended_cipher(use_case)
    cipher = cipher_registry.get_cipher(cipher_type)
    security_log("ENCRYPT_ATTEMPT", f"Using cipher: {cipher_type.name}, version: {version}, use_case: {use_case}", 
                 module="crypto.ciphers")
    return cipher.encrypt(data, key, version)

def smart_decrypt(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Automatically detect cipher type and decrypt"""
    from ...logging_service import security_log
    from ..exceptions import DecryptionError
    
    try:
        cipher_type = cipher_registry.detect_cipher_type(encrypted_data)
        cipher = cipher_registry.get_cipher(cipher_type)
        security_log("DECRYPT_ATTEMPT", f"Using cipher: {cipher_type.name}, version: {version}", 
                     module="crypto.ciphers")
        return cipher.decrypt(encrypted_data, key, version)
    except Exception as e:
        security_log("SMART_DECRYPT_ERROR", f"Smart decrypt failed: {str(e)}", 
                     module="crypto.ciphers")
        raise DecryptionError(f"Smart decrypt failed: {str(e)}")

# Expose public API
__all__ = [
    # Types and interfaces
    'CipherType',
    'CipherInterface',
    'CipherRegistry',
    'cipher_registry',
    
    # Cipher implementations
    'AESGCMCipher',
    'ChaCha20Poly1305Cipher', 
    'XChaCha20Poly1305Cipher',
    'AESSIVCipher',
    'CamelliaGCMCipher',
    'LayeredCipher',
    
    # Encryption functions
    'encrypt_aes_gcm',
    'encrypt_chacha20_poly1305',
    'encrypt_xchacha20_poly1305',
    'encrypt_aes_siv',
    'layered_encrypt',
    'smart_encrypt',
    
    # Decryption functions
    'decrypt_aes_gcm',
    'decrypt_chacha20_poly1305',
    'decrypt_xchacha20_poly1305',
    'decrypt_aes_siv',
    'layered_decrypt',
    'smart_decrypt',
    
    # Emergency decryption
    'emergency_decrypt',
    'emergency_decrypt_with_fallback',
    'get_emergency_decrypt_info',
]