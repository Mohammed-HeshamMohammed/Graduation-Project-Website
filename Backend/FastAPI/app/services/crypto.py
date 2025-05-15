# app/services/crypto.py
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config import settings
import hashlib

def derive_key(key_material: str) -> bytes:
    """
    Derives a secure encryption key from the provided key material using PBKDF2
    """
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

def encrypt_data(data: bytes) -> bytes:
    """
    Encrypts data using AES-256 encryption with proper key derivation
    """
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

def decrypt_data(encrypted_data: bytes) -> bytes:
    """
    Decrypts AES-256 encrypted data with proper key derivation
    """
    # Derive the same secure key
    key = derive_key(settings.ENCRYPTION_KEY)
    
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
        raise ValueError(f"Decryption failed. Data may be corrupted or tampered with: {str(e)}")