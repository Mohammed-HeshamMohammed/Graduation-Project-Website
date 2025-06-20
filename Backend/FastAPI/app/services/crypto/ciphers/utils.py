# ciphers/utils.py
"""
Utility functions for cipher operations.
"""

from typing import Tuple, Optional
from .types import CipherType, VERSION_SIZE, TYPE_SIZE, NONCE_SIZE, TAG_SIZE, MIN_ENCRYPTED_SIZE, get_nonce_size_for_cipher
from ..exceptions import DecryptionError

def validate_encrypted_data(data: bytes, min_size: int = MIN_ENCRYPTED_SIZE) -> None:
    """Validate encrypted data has minimum required size"""
    if len(data) < min_size:
        raise DecryptionError(f"Encrypted data too short: {len(data)} < {min_size}")

def split_encrypted_data(data: bytes, has_version: bool = True, cipher_type: Optional[CipherType] = None) -> Tuple[bytes, bytes, bytes, bytes]:
    """Split encrypted data into components: (version, nonce, tag, ciphertext)"""
    if has_version:
        validate_encrypted_data(data)
        version = data[:VERSION_SIZE]
        
        # Determine nonce size based on cipher type
        if cipher_type is None:
            # Try to detect cipher type from data
            type_byte = data[VERSION_SIZE:VERSION_SIZE + TYPE_SIZE]
            for ct in CipherType:
                if ct.value == type_byte:
                    cipher_type = ct
                    break
        
        nonce_size = get_nonce_size_for_cipher(cipher_type) if cipher_type else NONCE_SIZE
        
        # Skip cipher type byte
        nonce_start = VERSION_SIZE + TYPE_SIZE
        nonce_end = nonce_start + nonce_size
        tag_end = nonce_end + TAG_SIZE
        
        nonce = data[nonce_start:nonce_end]
        tag = data[nonce_end:tag_end]
        ciphertext = data[tag_end:]
    else:
        # Legacy format without version
        nonce_size = NONCE_SIZE  # Legacy always used 12-byte nonces
        min_legacy_size = nonce_size + TAG_SIZE
        if len(data) < min_legacy_size:
            raise DecryptionError(f"Legacy encrypted data too short: {len(data)} < {min_legacy_size}")
        version = b''
        nonce = data[:nonce_size]
        tag = data[nonce_size:nonce_size + TAG_SIZE]
        ciphertext = data[nonce_size + TAG_SIZE:]
    
    return version, nonce, tag, ciphertext