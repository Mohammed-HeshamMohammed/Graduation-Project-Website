# ciphers/xchacha20.py
"""
XChaCha20-Poly1305 cipher implementation - Best for real-time applications.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305
from .base import CipherInterface
from .types import CipherType, pack_version, XCHACHA_NONCE_SIZE, TAG_SIZE
from .utils import split_encrypted_data
from ..exceptions import EncryptionError, DecryptionError
from ...logging_service import security_log

class XChaCha20Poly1305Cipher(CipherInterface):
    """XChaCha20-Poly1305 cipher implementation - Best for real-time applications"""
    
    @property
    def cipher_type(self) -> CipherType:
        return CipherType.XCHACHA20_POLY1305
    
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Encrypt data using XChaCha20-Poly1305"""
        try:
            nonce = os.urandom(XCHACHA_NONCE_SIZE)  # 24-byte nonce
            cipher = XChaCha20Poly1305(key)
            
            version_bytes = pack_version(version)
            ciphertext = cipher.encrypt(nonce, data, version_bytes)
            
            # Extract tag (last 16 bytes) and actual ciphertext
            tag = ciphertext[-TAG_SIZE:]
            actual_ciphertext = ciphertext[:-TAG_SIZE]
            
            return version_bytes + self.cipher_type.value + nonce + tag + actual_ciphertext
        except Exception as e:
            security_log("ENCRYPTION_ERROR", f"XChaCha20-Poly1305 encryption error: {str(e)}", module="crypto.ciphers.xchacha20")
            raise EncryptionError(f"XChaCha20-Poly1305 encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt XChaCha20-Poly1305 encrypted data"""
        try:
            version_bytes, nonce, tag, ciphertext = split_encrypted_data(encrypted_data, cipher_type=self.cipher_type)
            
            cipher = XChaCha20Poly1305(key)
            # Reconstruct the format expected by cryptography library (ciphertext + tag)
            combined_data = ciphertext + tag
            
            return cipher.decrypt(nonce, combined_data, version_bytes)
        except Exception as e:
            security_log("DECRYPTION_ERROR", f"XChaCha20-Poly1305 decryption error: {str(e)}", module="crypto.ciphers.xchacha20")
            raise DecryptionError(f"XChaCha20-Poly1305 decryption failed: {str(e)}")

