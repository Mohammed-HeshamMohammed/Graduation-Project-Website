# ciphers/types.py
"""
Cipher types, constants, and data structures.
"""

import struct
from enum import Enum
from typing import Optional

class CipherType(Enum):
    """Cipher type identifiers"""
    AES_GCM = b'\x00'
    CHACHA20_POLY1305 = b'\x01'
    LAYERED = b'\x02'
    XCHACHA20_POLY1305 = b'\x03'
    AES_SIV = b'\x04'
    CAMELLIA_GCM = b'\x05'
    TWOFISH_CTR = b'\x06'

# Constants for data structure
VERSION_SIZE = 4
TYPE_SIZE = 1
NONCE_SIZE = 12
XCHACHA_NONCE_SIZE = 24  # XChaCha20 uses 24-byte nonces
TAG_SIZE = 16
MIN_ENCRYPTED_SIZE = VERSION_SIZE + TYPE_SIZE + NONCE_SIZE + TAG_SIZE

def pack_version(version: int) -> bytes:
    """Pack version number into bytes"""
    return struct.pack('>I', version)

def unpack_version(data: bytes) -> int:
    """Unpack version number from bytes"""
    return struct.unpack('>I', data[:VERSION_SIZE])[0]

def get_nonce_size_for_cipher(cipher_type: CipherType) -> int:
    """Get the appropriate nonce size for the cipher type"""
    if cipher_type == CipherType.XCHACHA20_POLY1305:
        return XCHACHA_NONCE_SIZE
    return NONCE_SIZE