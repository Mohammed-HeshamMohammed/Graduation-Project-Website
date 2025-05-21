# app/services/crypto/ciphers.py
import os
import struct
import hashlib
import time
from typing import Tuple

from Crypto.Cipher import AES, ChaCha20_Poly1305
from app.services.logging_service import get_module_logger, security_log
from app.middleware.security import rate_limit

from .constants import (
    CIPHER_AES_GCM, CIPHER_CHACHA20_POLY1305, CIPHER_LAYERED
)
from .exceptions import DecryptionError, EncryptionError
from .utils import derive_key, extract_version

logger = get_module_logger("crypto.ciphers", log_to_file=True)

def encrypt_aes_gcm(data: bytes, key: bytes, version: int) -> bytes:
    """Encrypt data using AES-256-GCM"""
    try:
        nonce = os.urandom(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        version_bytes = struct.pack('>I', version)
        cipher.update(version_bytes)
        
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        return version_bytes + CIPHER_AES_GCM + nonce + tag + ciphertext
    except Exception as e:
        security_log("ENCRYPTION_ERROR", f"AES-GCM encryption error: {str(e)}", module="crypto.ciphers")
        raise EncryptionError(f"AES-GCM encryption failed: {str(e)}")

def encrypt_chacha20_poly1305(data: bytes, key: bytes, version: int) -> bytes:
    """Encrypt data using ChaCha20-Poly1305"""
    try:
        nonce = os.urandom(12)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        
        version_bytes = struct.pack('>I', version)
        cipher.update(version_bytes)
        
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        return version_bytes + CIPHER_CHACHA20_POLY1305 + nonce + tag + ciphertext
    except Exception as e:
        security_log("ENCRYPTION_ERROR", f"ChaCha20-Poly1305 encryption error: {str(e)}", module="crypto.ciphers")
        raise EncryptionError(f"ChaCha20-Poly1305 encryption failed: {str(e)}")

def decrypt_aes_gcm(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt AES-256-GCM encrypted data"""
    try:
        nonce = encrypted_data[1:13]
        tag = encrypted_data[13:29]
        ciphertext = encrypted_data[29:]
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        version_bytes = struct.pack('>I', version)
        cipher.update(version_bytes)
        
        return cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        security_log("DECRYPTION_ERROR", f"AES-GCM decryption error: {str(e)}", module="crypto.ciphers")
        raise DecryptionError(f"AES-GCM decryption failed: {str(e)}")

def decrypt_chacha20_poly1305(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt ChaCha20-Poly1305 encrypted data"""
    try:
        nonce = encrypted_data[1:13]
        tag = encrypted_data[13:29]
        ciphertext = encrypted_data[29:]
        
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        
        version_bytes = struct.pack('>I', version)
        cipher.update(version_bytes)
        
        return cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        security_log("DECRYPTION_ERROR", f"ChaCha20-Poly1305 decryption error: {str(e)}", module="crypto.ciphers")
        raise DecryptionError(f"ChaCha20-Poly1305 decryption failed: {str(e)}")

def layered_encrypt(data: bytes, key: bytes, version: int) -> bytes:
    """Apply multiple layers of encryption for added security"""
    try:
        # First layer - ChaCha20-Poly1305
        chacha_key = hashlib.sha256(key + b"chacha_layer").digest()
        encrypted = encrypt_chacha20_poly1305(data, chacha_key, version)
        
        # Second layer - AES-GCM
        aes_key = hashlib.sha256(key + b"aes_layer").digest()
        encrypted = encrypt_aes_gcm(encrypted, aes_key, version)
        
        # Mark as layered encryption with a prefix byte
        return b'\xFF' + encrypted
    except Exception as e:
        security_log("ENCRYPTION_ERROR", f"Layered encryption error: {str(e)}", module="crypto.ciphers")
        raise EncryptionError(f"Layered encryption failed: {str(e)}")

def layered_decrypt(encrypted_data: bytes, key: bytes, version: int) -> bytes:
    """Decrypt multiple layers of encryption"""
    try:
        # Remove the layered marker byte
        encrypted_data = encrypted_data[1:]
        
        # Second layer - AES-GCM
        aes_key = hashlib.sha256(key + b"aes_layer").digest()
        decrypted = decrypt_aes_gcm(encrypted_data, aes_key, version)
        
        # First layer - ChaCha20-Poly1305
        chacha_key = hashlib.sha256(key + b"chacha_layer").digest()
        return decrypt_chacha20_poly1305(decrypted, chacha_key, version)
    except Exception as e:
        security_log("DECRYPTION_ERROR", f"Layered decryption error: {str(e)}", module="crypto.ciphers")
        raise DecryptionError(f"Layered decryption failed: {str(e)}")

def emergency_decrypt(data: bytes, client_ip: str = '0.0.0.0') -> bytes:
    """Last resort decryption attempt with multiple formats and legacy handling"""
    security_log("EMERGENCY", "Attempting emergency decryption", module="crypto.ciphers")
    
    from app.config import settings
    
    # Try with default version 1
    key = derive_key(settings.ENCRYPTION_KEY, 1)
    
    # Try legacy format (no version prefix)
    if len(data) >= 28:  # Minimum size for nonce + tag + some data
        try:
            # Legacy format without version and with direct AES-GCM
            nonce = data[:12]
            tag = data[12:28]
            ciphertext = data[28:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except:
            pass
    
    # Try with version but wrong cipher type identification
    if len(data) >= 33:  # 4 (version) + 1 (type) + 12 (nonce) + 16 (tag)
        version_bytes = data[:4]
        try:
            version = struct.unpack('>I', version_bytes)[0]
            if 0 < version < 100:  # Reasonable version range
                key = derive_key(settings.ENCRYPTION_KEY, version)
                
                # Try AES-GCM format
                try:
                    nonce = data[5:17]
                    tag = data[17:33]
                    ciphertext = data[33:]
                    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
                    cipher.update(version_bytes)
                    return cipher.decrypt_and_verify(ciphertext, tag)
                except:
                    pass
                    
                # Try ChaCha20-Poly1305 format
                try:
                    nonce = data[5:17]
                    tag = data[17:33]
                    ciphertext = data[33:]
                    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
                    cipher.update(version_bytes)
                    return cipher.decrypt_and_verify(ciphertext, tag)
                except:
                    pass
        except: 
            pass
    
    raise DecryptionError("Emergency decryption failed with all attempts")