import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from app.config import settings

def encrypt_data(data: bytes) -> bytes:
    """
    Encrypts data using AES-256 encryption
    """
    key = settings.ENCRYPTION_KEY.encode('utf-8')
    # Ensure key is exactly 32 bytes (256 bits)
    key = key[:32].ljust(32, b'\0')
    
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
    Decrypts AES-256 encrypted data
    """
    key = settings.ENCRYPTION_KEY.encode('utf-8')
    # Ensure key is exactly 32 bytes (256 bits)
    key = key[:32].ljust(32, b'\0')
    
    # Extract IV from the first 16 bytes
    iv = encrypted_data[:16]
    actual_data = encrypted_data[16:]
    
    # Create cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt and unpad
    decrypted_data = unpad(cipher.decrypt(actual_data), AES.block_size)
    
    return decrypted_data