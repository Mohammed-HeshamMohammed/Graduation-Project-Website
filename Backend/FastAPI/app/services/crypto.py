# app/services/crypto.py
import base64
import os
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config import settings
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

def derive_key(key_material: str) -> bytes:
    """
    Derives a secure encryption key from the provided key material using PBKDF2
    """
    try:
        # Use a fixed salt for reproducibility - in production, consider using a secure stored salt
        salt = b'anthropic_claude_salt'
        
        # Use PBKDF2 via hashlib to derive a secure key
        key = hashlib.pbkdf2_hmac(
            'sha256',                  # Hash algorithm
            key_material.encode(),     # Convert password to bytes
            salt,                      # Salt
            100000,                    # Number of iterations (higher is more secure but slower)
            dklen=32                   # Length of the key (32 bytes = 256 bits)
        )
        
        return key
    except Exception as e:
        logger.error(f"Error deriving encryption key: {type(e).__name__}: {e}")
        raise

def encrypt_data(data: bytes) -> bytes:
    """
    Encrypts data using AES-256 encryption with proper key derivation
    """
    try:
        # Derive a secure key from the configuration key
        key = derive_key(settings.ENCRYPTION_KEY)
        
        iv = os.urandom(16)  # Generate random initialization vector
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad the data to be a multiple of block size
        padded_data = pad(data, AES.block_size)
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(padded_data)
        
        # Return IV + encrypted data
        return iv + encrypted_data
    except Exception as e:
        logger.error(f"Encryption error: {type(e).__name__}: {e}")
        raise

def decrypt_data(encrypted_data: bytes) -> bytes:
    """
    Decrypts AES-256 encrypted data with proper key derivation
    """
    try:
        # Derive the same secure key
        key = derive_key(settings.ENCRYPTION_KEY)
        
        # Check if data is too short
        if len(encrypted_data) < 16:
            raise ValueError("Encrypted data is too short to contain IV")
        
        # Extract IV from the first 16 bytes
        iv = encrypted_data[:16]
        actual_data = encrypted_data[16:]
        
        # Create cipher object
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        try:
            decrypted_data = unpad(cipher.decrypt(actual_data), AES.block_size)
            return decrypted_data
        except (ValueError, KeyError) as e:
            # Handle padding errors which could indicate tampering
            logger.error(f"Decryption padding error: {str(e)}")
            raise ValueError(f"Decryption failed. Data may be corrupted or tampered with: {str(e)}")
    except Exception as e:
        logger.error(f"Decryption error: {type(e).__name__}: {e}")
        raise