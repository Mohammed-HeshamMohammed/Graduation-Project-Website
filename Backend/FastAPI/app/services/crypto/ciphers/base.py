# ciphers/base.py
"""
Abstract base class for cipher implementations.
"""

from abc import ABC, abstractmethod
from .types import CipherType

class CipherInterface(ABC):
    """Abstract base class for all ciphers"""
    
    @abstractmethod
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Encrypt data and return encrypted bytes"""
        pass
    
    @abstractmethod
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt encrypted data and return original bytes"""
        pass
    
    @property
    @abstractmethod
    def cipher_type(self) -> CipherType:
        """Return the cipher type identifier"""
        pass