# ciphers/chacha20.py
"""
ChaCha20-Poly1305 cipher implementation.
"""

import os
from Crypto.Cipher import ChaCha20_Poly1305
from .base import CipherInterface
from .types import CipherType, pack_version, NONCE_SIZE
from .utils import split_encrypted_data
from ..exceptions import EncryptionError, DecryptionError
from ...logging_service import security_log

class ChaCha20Poly1305Cipher(CipherInterface):
    """ChaCha20-Poly1305 cipher implementation"""
    
    @property
    def cipher_type(self) -> CipherType:
        return CipherType.CHACHA20_POLY1305
    
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Encrypt data using ChaCha20-Poly1305"""
        try:
            nonce = os.urandom(NONCE_SIZE)
            cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
            
            version_bytes = pack_version(version)
            cipher.update(version_bytes)
            
            ciphertext, tag = cipher.encrypt_and_digest(data)
            
            return version_bytes + self.cipher_type.value + nonce + tag + ciphertext
        except Exception as e:
            security_log("ENCRYPTION_ERROR", f"ChaCha20-Poly1305 encryption error: {str(e)}", module="crypto.ciphers.chacha20")
            raise EncryptionError(f"ChaCha20-Poly1305 encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt ChaCha20-Poly1305 encrypted data"""
        try:
            version_bytes, nonce, tag, ciphertext = split_encrypted_data(encrypted_data, cipher_type=self.cipher_type)
            
            cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
            cipher.update(version_bytes)
            
            return cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            security_log("DECRYPTION_ERROR", f"ChaCha20-Poly1305 decryption error: {str(e)}", module="crypto.ciphers.chacha20")
            raise DecryptionError(f"ChaCha20-Poly1305 decryption failed: {str(e)}")

