# ciphers/aes_gcm.py
"""
AES-256-GCM cipher implementation.
"""

import os
from Crypto.Cipher import AES
from .base import CipherInterface
from .types import CipherType, pack_version, NONCE_SIZE
from .utils import split_encrypted_data
from ..exceptions import EncryptionError, DecryptionError
from ...logging_service import security_log

class AESGCMCipher(CipherInterface):
    """AES-256-GCM cipher implementation"""
    
    @property
    def cipher_type(self) -> CipherType:
        return CipherType.AES_GCM
    
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Encrypt data using AES-256-GCM"""
        try:
            nonce = os.urandom(NONCE_SIZE)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            
            version_bytes = pack_version(version)
            cipher.update(version_bytes)
            
            ciphertext, tag = cipher.encrypt_and_digest(data)
            
            return version_bytes + self.cipher_type.value + nonce + tag + ciphertext
        except Exception as e:
            security_log("ENCRYPTION_ERROR", f"AES-GCM encryption error: {str(e)}", module="crypto.ciphers.aes_gcm")
            raise EncryptionError(f"AES-GCM encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt AES-256-GCM encrypted data"""
        try:
            version_bytes, nonce, tag, ciphertext = split_encrypted_data(encrypted_data, cipher_type=self.cipher_type)
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            cipher.update(version_bytes)
            
            return cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            security_log("DECRYPTION_ERROR", f"AES-GCM decryption error: {str(e)}", module="crypto.ciphers.aes_gcm")
            raise DecryptionError(f"AES-GCM decryption failed: {str(e)}")

