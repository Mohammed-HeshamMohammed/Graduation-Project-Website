# ciphers/layered.py
"""
Layered encryption using multiple cipher types for enhanced security.
"""

import hashlib
from .base import CipherInterface
from .types import CipherType, pack_version, VERSION_SIZE, TYPE_SIZE
from .aes_gcm import AESGCMCipher
from .xchacha20 import XChaCha20Poly1305Cipher
from ..exceptions import EncryptionError, DecryptionError
from ...logging_service import security_log

class LayeredCipher(CipherInterface):
    """Layered encryption using multiple cipher types"""
    
    def __init__(self):
        self.aes_cipher = AESGCMCipher()
        self.xchacha_cipher = XChaCha20Poly1305Cipher()
    
    @property
    def cipher_type(self) -> CipherType:
        return CipherType.LAYERED
    
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Apply multiple layers of encryption for added security"""
        try:
            # First layer - XChaCha20-Poly1305 (better for real-time)
            xchacha_key = hashlib.sha256(key + b"xchacha_layer").digest()
            encrypted = self.xchacha_cipher.encrypt(data, xchacha_key, version)
            
            # Second layer - AES-GCM
            aes_key = hashlib.sha256(key + b"aes_layer").digest()
            encrypted = self.aes_cipher.encrypt(encrypted, aes_key, version)
            
            # Mark as layered encryption by replacing the cipher type
            version_bytes = pack_version(version)
            return version_bytes + self.cipher_type.value + encrypted[VERSION_SIZE + TYPE_SIZE:]
        except Exception as e:
            security_log("ENCRYPTION_ERROR", f"Layered encryption error: {str(e)}", module="crypto.ciphers.layered")
            raise EncryptionError(f"Layered encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt multiple layers of encryption"""
        try:
            # Reconstruct the AES layer format
            version_bytes = encrypted_data[:VERSION_SIZE]
            aes_data = version_bytes + CipherType.AES_GCM.value + encrypted_data[VERSION_SIZE + TYPE_SIZE:]
            
            # Second layer - AES-GCM
            aes_key = hashlib.sha256(key + b"aes_layer").digest()
            decrypted = self.aes_cipher.decrypt(aes_data, aes_key, version)
            
            # First layer - XChaCha20-Poly1305
            xchacha_key = hashlib.sha256(key + b"xchacha_layer").digest()
            return self.xchacha_cipher.decrypt(decrypted, xchacha_key, version)
        except Exception as e:
            security_log("DECRYPTION_ERROR", f"Layered decryption error: {str(e)}", module="crypto.ciphers.layered")
            raise DecryptionError(f"Layered decryption failed: {str(e)}")

