# app/services/crypto/utils.py
import hashlib
import struct
from typing import Optional, Tuple

from app.services.logging_service import get_module_logger, security_log
from app.middleware.security import validate_input, rate_limit
from .exceptions import CryptoException

logger = get_module_logger("crypto.utils", log_to_file=True)

def derive_key(key_material: str, version: int) -> bytes:
    """Derive a secure encryption key from the provided key material with versioning"""
    try:
        # Use a fixed salt for reproducibility
        salt = b'anthropic_claude_salt' + str(version).encode()
        
        # Incorporate version into key derivation
        version_str = f"v{version}_{key_material}"
        
        # Use PBKDF2 via hashlib to derive a secure key
        key = hashlib.pbkdf2_hmac(
            'sha256',
            version_str.encode(),
            salt,
            100000,
            dklen=32
        )
        
        return key
    except Exception as e:
        security_log("KEY_ERROR", f"Error deriving encryption key: {type(e).__name__}: {e}", module="crypto.utils")
        raise

def extract_version(encrypted_data: bytes) -> Tuple[int, bytes]:
    """Extract version from encrypted data"""
    if len(encrypted_data) < 5:
        raise ValueError("Encrypted data is too short")
    
    version_bytes = encrypted_data[:4]
    version = struct.unpack('>I', version_bytes)[0]
    return version, version_bytes