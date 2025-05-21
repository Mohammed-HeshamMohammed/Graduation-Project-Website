# app/services/crypto/obfuscation.py
from typing import Dict, Union

def transform_data(data: bytes, is_encrypt: bool) -> bytes:
    """Either obfuscate or deobfuscate data based on is_encrypt flag"""
    obfuscation_key = b'\x87\x32\xA9\xF1\x55\xCE\x3B\xD6\xC0\xE4\x19\x7A\x8D\x2F\xB5\x64'
    result = bytearray(len(data))
    
    for i in range(len(data)):
        key_byte = obfuscation_key[i % len(obfuscation_key)]
        shift = (i % 11) + (i % 7) + (i % 5)
        
        if is_encrypt:
            # Obfuscate
            result[i] = ((data[i] ^ key_byte) + shift) % 256
        else:
            # Deobfuscate
            result[i] = ((data[i] - shift) % 256) ^ key_byte
        
    return bytes(result)

def obfuscate_data(data: bytes) -> bytes:
    """Obfuscate data with XOR and byte shifting"""
    return transform_data(data, True)

def deobfuscate_data(data: bytes) -> bytes:
    """Reverse the obfuscation process"""
    return transform_data(data, False)