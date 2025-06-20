# ciphers/registry.py
"""
Registry for managing cipher implementations.
"""

from typing import Dict
from .base import CipherInterface
from .types import CipherType
from .utils import validate_encrypted_data
from ..exceptions import DecryptionError, EncryptionError
from ...logging_service import get_module_logger

logger = get_module_logger("crypto.ciphers.registry", log_to_file=True)

class CipherRegistry:
    """Registry for managing cipher implementations"""
    
    def __init__(self):
        self._ciphers: Dict[CipherType, CipherInterface] = {}
    
    def register(self, cipher: CipherInterface):
        """Register a cipher implementation"""
        self._ciphers[cipher.cipher_type] = cipher
        logger.info(f"Registered cipher: {cipher.cipher_type.name}")
    
    def get_cipher(self, cipher_type: CipherType) -> CipherInterface:
        """Get cipher implementation by type"""
        if cipher_type not in self._ciphers:
            raise EncryptionError(f"Unsupported cipher type: {cipher_type}")
        return self._ciphers[cipher_type]
    
    def detect_cipher_type(self, encrypted_data: bytes) -> CipherType:
        """Detect cipher type from encrypted data"""
        from .types import VERSION_SIZE, TYPE_SIZE
        validate_encrypted_data(data=encrypted_data, min_size=VERSION_SIZE + TYPE_SIZE + 1)
        
        type_byte = encrypted_data[VERSION_SIZE:VERSION_SIZE + TYPE_SIZE]
        for cipher_type in CipherType:
            if cipher_type.value == type_byte:
                return cipher_type
        
        raise DecryptionError(f"Unknown cipher type: {type_byte}")
    
    def get_recommended_cipher(self, use_case: str = "general") -> CipherType:
        """Get recommended cipher type based on use case"""
        recommendations = {
            "realtime": CipherType.XCHACHA20_POLY1305,  # Best for real-time with long nonces
            "deterministic": CipherType.AES_SIV,        # Nonce-reuse resistant
            "high_security": CipherType.LAYERED,        # Multiple layers
            "general": CipherType.XCHACHA20_POLY1305,   # Good default choice
            "legacy": CipherType.AES_GCM,               # Backward compatibility
        }
        return recommendations.get(use_case, CipherType.XCHACHA20_POLY1305)

# Global cipher registry instance
cipher_registry = CipherRegistry()