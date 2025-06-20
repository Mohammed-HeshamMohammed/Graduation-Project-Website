# ciphers/camellia.py
"""
Camellia-GCM cipher implementation - AES alternative for layered security.
"""

import os
from .base import CipherInterface
from .types import CipherType, pack_version, NONCE_SIZE, TAG_SIZE
from .utils import split_encrypted_data
from ..exceptions import EncryptionError, DecryptionError
from ...logging_service import security_log

class CamelliaGCMCipher(CipherInterface):
    """Camellia-GCM cipher implementation - AES alternative for layered security"""
    
    @property
    def cipher_type(self) -> CipherType:
        return CipherType.CAMELLIA_GCM
    
    def encrypt(self, data: bytes, key: bytes, version: int) -> bytes:
        """Encrypt data using Camellia-GCM"""
        try:
            # Note: This requires the cryptography library with Camellia support
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            nonce = os.urandom(NONCE_SIZE)
            cipher = Cipher(algorithms.Camellia(key), modes.GCM(nonce), backend=default_backend())
            encryptor = cipher.encryptor()
            
            version_bytes = pack_version(version)
            encryptor.authenticate_additional_data(version_bytes)
            
            ciphertext = encryptor.update(data) + encryptor.finalize()
            tag = encryptor.tag
            
            return version_bytes + self.cipher_type.value + nonce + tag + ciphertext
        except ImportError:
            raise EncryptionError("Camellia cipher not available. Install cryptography with Camellia support.")
        except Exception as e:
            security_log("ENCRYPTION_ERROR", f"Camellia-GCM encryption error: {str(e)}", module="crypto.ciphers.camellia")
            raise EncryptionError(f"Camellia-GCM encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, key: bytes, version: int) -> bytes:
        """Decrypt Camellia-GCM encrypted data"""
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            version_bytes, nonce, tag, ciphertext = split_encrypted_data(encrypted_data, cipher_type=self.cipher_type)
            
            cipher = Cipher(algorithms.Camellia(key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decryptor.authenticate_additional_data(version_bytes)
            
            return decryptor.update(ciphertext) + decryptor.finalize()
        except ImportError:
            raise DecryptionError("Camellia cipher not available. Install cryptography with Camellia support.")
        except Exception as e:
            security_log("DECRYPTION_ERROR", f"Camellia-GCM decryption error: {str(e)}", module="crypto.ciphers.camellia")
            raise DecryptionError(f"Camellia-GCM decryption failed: {str(e)}")

