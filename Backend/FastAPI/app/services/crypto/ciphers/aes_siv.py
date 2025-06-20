# ciphers/aes_siv.py
"""
AES-SIV cipher implementation - Deterministic and nonce-reuse resistant.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from .base import CipherInterface
from .types import CipherType, pack_version, NONCE_SIZE
from .utils import split_encrypted_data
from ..exceptions import EncryptionError, DecryptionError
from ...logging_service import security_log

class AESSIVCipher(CipherInterface):
    """AES-SIV cipher implementation - Deterministic and nonce-reuse resistant"""
    
    @property
    def cipher_type(self) -> CipherType:
        return CipherType.AES_SIV
    
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Encrypt data using AES-SIV"""
        try:
            # AES-SIV doesn't use traditional nonces, but we'll generate one for consistency
            nonce = os.urandom(NONCE_SIZE)
            cipher = AESSIV(key)
            
            version_bytes = pack_version(version)
            # AES-SIV uses associated data instead of updating cipher
            ciphertext = cipher.encrypt(data, [version_bytes, nonce])
            
            # AES-SIV output includes the SIV (synthetic IV) at the beginning
            siv = ciphertext[:16]  # First 16 bytes are the SIV
            actual_ciphertext = ciphertext[16:]
            
            return version_bytes + self.cipher_type.value + nonce + siv + actual_ciphertext
        except Exception as e:
            security_log("ENCRYPTION_ERROR", f"AES-SIV encryption error: {str(e)}", module="crypto.ciphers.aes_siv")
            raise EncryptionError(f"AES-SIV encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt AES-SIV encrypted data"""
        try:
            version_bytes, nonce, siv, ciphertext = split_encrypted_data(encrypted_data, cipher_type=self.cipher_type)
            
            cipher = AESSIV(key)
            # Reconstruct the SIV format (SIV + ciphertext)
            combined_data = siv + ciphertext
            
            return cipher.decrypt(combined_data, [version_bytes, nonce])
        except Exception as e:
            security_log("DECRYPTION_ERROR", f"AES-SIV decryption error: {str(e)}", module="crypto.ciphers.aes_siv")
            raise DecryptionError(f"AES-SIV decryption failed: {str(e)}")

