# app/services/crypto/integrity.py
import hashlib
import base64
from typing import Dict, Union, Optional
from Crypto.Hash import HMAC, SHA256

from app.services.logging_service import get_module_logger, security_log
from app.config import settings
from .utils import derive_key

logger = get_module_logger("crypto.integrity", log_to_file=True)

def calculate_hmac(data: bytes, key: bytes) -> bytes:
    """Calculate HMAC for data integrity verification"""
    h = HMAC.new(key, digestmod=SHA256)
    h.update(data)
    return h.digest()

def verify_hmac(data: bytes, signature: bytes, key: bytes) -> bool:
    """Verify HMAC signature"""
    h = HMAC.new(key, digestmod=SHA256)
    h.update(data)
    try:
        h.verify(signature)
        return True
    except ValueError:
        return False

def get_hmac_key() -> bytes:
    """Generate a key for HMAC operations"""
    return derive_key(settings.ENCRYPTION_KEY + "_hmac", 0)

def manage_canary_values(data_dict: Dict, verify: bool = False) -> Union[Dict, bool]:
    """Add or verify canary values for tamper detection"""
    if verify:
        # Verify mode
        if '_canary' not in data_dict:
            return False
        
        for key, value in data_dict.items():
            if isinstance(value, dict) and len(value) > 0 and '_nested_canary' in value:
                canary_value = data_dict['_canary']
                expected_nested = hashlib.sha256((canary_value + str(key)).encode()).digest()[:8]
                expected_nested = base64.b64encode(expected_nested).decode('ascii')
                
                if value['_nested_canary'] != expected_nested:
                    return False
        
        return True
    else:
        # Add mode
        canary_base = hashlib.sha256(str(data_dict).encode()).digest()[:12]
        canary_value = base64.b64encode(canary_base).decode('ascii')
        
        data_dict['_canary'] = canary_value
        
        for key, value in data_dict.items():
            if isinstance(value, dict) and len(value) > 0:
                nested_canary = hashlib.sha256((canary_value + str(key)).encode()).digest()[:8]
                data_dict[key]['_nested_canary'] = base64.b64encode(nested_canary).decode('ascii')
        
        return data_dict

def add_canary_values(data_dict: Dict) -> Dict:
    """Add canary values to detect tampering in dictionary structures"""
    return manage_canary_values(data_dict, False)

def verify_canary_values(data_dict: Dict) -> bool:
    """Verify canary values to detect tampering"""
    return manage_canary_values(data_dict, True)