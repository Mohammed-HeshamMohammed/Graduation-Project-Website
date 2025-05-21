# app/services/crypto/constants.py
from pathlib import Path

# Key rotation constants
MIN_ROTATION_DAYS = 1  # Minimum days before rotation
MAX_ROTATION_DAYS = 5  # Maximum days before rotation
KEY_STORAGE_FILE = Path("keys/keystore.bin")
KEY_STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Magic bytes for file format validation
MAGIC_HEADER = b'\xAE\x7F\xD2\x91\xB4\x33\xE5\xC8'

# Encryption configuration
DEFAULT_CIPHER = "AES_GCM"
LAYERED_ENCRYPTION = True
USE_CHACHA = True

# Anti-tampering configuration
HMAC_VERIFICATION = True
CANARY_VALUES = True

# Cipher type identifiers
CIPHER_AES_GCM = b'\x00'
CIPHER_CHACHA20_POLY1305 = b'\x01'
CIPHER_LAYERED = b'\xFF'