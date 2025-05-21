# app/services/crypto/key_management.py
import os
import time
import datetime
import random
import struct
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Optional

from app.services.logging_service import get_module_logger, security_log
from app.config import settings
from .constants import (
    KEY_STORAGE_FILE, MIN_ROTATION_DAYS, MAX_ROTATION_DAYS, 
    MAGIC_HEADER, HMAC_VERIFICATION, CANARY_VALUES
)
from .utils import derive_key
from .integrity import calculate_hmac, verify_hmac, add_canary_values, verify_canary_values, get_hmac_key
from .obfuscation import obfuscate_data, deobfuscate_data
from .exceptions import KeyManagementError, TamperingDetected, FileFormatError

logger = get_module_logger("crypto.key_management", log_to_file=True)

def write_key_data(key_data: Dict) -> None:
    """Write key data to binary file with custom format and enhanced security"""
    try:
        # Add canary values for tampering detection
        if CANARY_VALUES:
            key_data = add_canary_values(key_data)
        
        # Convert key data to bytes
        serialized_data = pickle.dumps(key_data)
        
        # Calculate primary checksum
        checksum = hashlib.sha256(serialized_data).digest()
        
        # Add HMAC signature if enabled
        if HMAC_VERIFICATION:
            hmac_key = get_hmac_key()
            hmac_signature = calculate_hmac(serialized_data, hmac_key)
        else:
            hmac_signature = b''
        
        # Obfuscate the data
        obfuscated_data = obfuscate_data(serialized_data)
        
        # Prepare header with size information and HMAC validation marker
        data_size = len(obfuscated_data)
        hmac_size = len(hmac_signature)
        header = struct.pack('>8sLL32s', MAGIC_HEADER, data_size, hmac_size, checksum)
        
        # Create backup file before writing
        if KEY_STORAGE_FILE.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backup_file = KEY_STORAGE_FILE.with_name(f"keystore_{timestamp}.bak")
            backup_file.write_bytes(KEY_STORAGE_FILE.read_bytes())
        
        # Write the file
        with open(KEY_STORAGE_FILE, 'wb') as f:
            f.write(header)
            f.write(hmac_signature)
            f.write(obfuscated_data)
            
    except Exception as e:
        security_log("FILE_ERROR", f"Error writing key data: {str(e)}", module="crypto.key_management")
        raise KeyManagementError(f"Failed to write key data: {str(e)}")

def read_key_data() -> Optional[Dict]:
    """Read key data from binary file with format validation and security checks"""
    if not KEY_STORAGE_FILE.exists():
        return None
    
    try:
        with open(KEY_STORAGE_FILE, 'rb') as f:
            # Read header
            header = f.read(8 + 4 + 4 + 32)
            
            if len(header) < 48:
                security_log("FILE_ERROR", "Corrupted key file (header too small)", module="crypto.key_management")
                raise FileFormatError("Corrupted key file (header too small)")
            
            magic, data_size, hmac_size, expected_checksum = struct.unpack('>8sLL32s', header)
            
            # Validate magic bytes
            if magic != MAGIC_HEADER:
                security_log("FILE_ERROR", "Invalid key file format", module="crypto.key_management")
                raise FileFormatError("Invalid key file format")
            
            # Read HMAC signature if present
            hmac_signature = f.read(hmac_size) if hmac_size > 0 else b''
            
            # Read data
            obfuscated_data = f.read(data_size)
            
            if len(obfuscated_data) != data_size:
                security_log("FILE_ERROR", "Corrupted key file (unexpected data size)", module="crypto.key_management")
                raise FileFormatError("Corrupted key file (unexpected data size)")
            
            # Deobfuscate data
            serialized_data = deobfuscate_data(obfuscated_data)
            
            # Verify checksum
            actual_checksum = hashlib.sha256(serialized_data).digest()
            if actual_checksum != expected_checksum:
                security_log("FILE_ERROR", "Key file integrity check failed", module="crypto.key_management")
                raise TamperingDetected("Key file integrity check failed")
            
            # Verify HMAC if present
            if HMAC_VERIFICATION and hmac_size > 0:
                hmac_key = get_hmac_key()
                if not verify_hmac(serialized_data, hmac_signature, hmac_key):
                    security_log("SECURITY_ERROR", "HMAC verification failed for key file", module="crypto.key_management")
                    raise TamperingDetected("HMAC verification failed for key file")
            
            # Deserialize data
            key_data = pickle.loads(serialized_data)
            
            # Verify canary values if enabled
            if CANARY_VALUES and not verify_canary_values(key_data):
                security_log("SECURITY_ERROR", "Canary value verification failed - possible tampering", module="crypto.key_management")
                raise TamperingDetected("Canary value verification failed - possible tampering")
            
            return key_data
            
    except (TamperingDetected, FileFormatError) as e:
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        security_log("FILE_ERROR", f"Error reading key file: {str(e)}", module="crypto.key_management")
        raise KeyManagementError(f"Failed to read key data: {str(e)}")

def get_current_key_version() -> int:
    """Get or create the current key version based on random rotation schedule"""
    try:
        # Read existing key data
        key_data = read_key_data()
        
        # Initialize if not exists
        if key_data is None:
            # Generate random next rotation time between MIN-MAX days
            next_rotation_seconds = random.randint(
                MIN_ROTATION_DAYS * 24 * 60 * 60, 
                MAX_ROTATION_DAYS * 24 * 60 * 60
            )
            
            key_data = {
                "current_version": 1,
                "last_rotation": time.time(),
                "next_rotation": time.time() + next_rotation_seconds,
                "history": {
                    "1": {"created_at": time.time()}
                }
            }
            write_key_data(key_data)
            security_log("KEY_ROTATION", "Initial key version created", module="crypto.key_management")
            return 1

        # Check if it's time for rotation
        current_time = time.time()
        if current_time >= key_data["next_rotation"]:
            # Generate new random rotation time
            next_rotation_seconds = random.randint(
                MIN_ROTATION_DAYS * 24 * 60 * 60, 
                MAX_ROTATION_DAYS * 24 * 60 * 60
            )
            
            # Update key version
            new_version = key_data["current_version"] + 1
            key_data["current_version"] = new_version
            key_data["last_rotation"] = current_time
            key_data["next_rotation"] = current_time + next_rotation_seconds
            key_data["history"][str(new_version)] = {"created_at": current_time}
            
            # Save updated key data
            write_key_data(key_data)
            
            # Log rotation event
            next_date = datetime.datetime.fromtimestamp(current_time + next_rotation_seconds).strftime("%Y-%m-%d %H:%M:%S")
            security_log("KEY_ROTATION", f"Key rotated to version {new_version}. Next rotation at {next_date}", module="crypto.key_management")
            
            return new_version
        
        return key_data["current_version"]
        
    except Exception as e:
        security_log("KEY_ERROR", f"Error in key version management: {str(e)}", module="crypto.key_management")
        # Failsafe: return version 1 if anything fails
        return 1