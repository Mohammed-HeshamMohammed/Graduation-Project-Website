"""
Message Storage Module

Handles encrypted storage and retrieval of user messages.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

from app.services.crypto import encrypt_data, decrypt_data, encrypt_with_failsafe, decrypt_with_failsafe, CryptoException
from app.config import settings

logger = logging.getLogger(__name__)


class MessageStorage:
    """Handles encrypted storage and retrieval of messages"""
    
    def __init__(self):
        """Initialize message storage"""
        self.data_dir = Path(settings.DATA_DIR)
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File path for messages
        self.messages_path = self.data_dir / "user_messages.enc"
    
    def load_messages(self) -> Dict[str, Any]:
        """Load user messages from encrypted file"""
        if not os.path.exists(self.messages_path):
            logger.info("Messages file does not exist, creating new messages store")
            return {}
        
        try:
            with open(self.messages_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return {}
                
                try:
                    decrypted_data = decrypt_with_failsafe(encrypted_data, client_ip='127.0.0.1')
                except CryptoException:
                    try:
                        decrypted_data = decrypt_data(encrypted_data, client_ip='127.0.0.1')
                    except CryptoException:
                        logger.warning("Unable to decrypt messages, starting fresh")
                        return {}
                
                messages = json.loads(decrypted_data.decode('utf-8'))
                logger.info(f"Loaded messages for {len(messages)} user(s)")
                return messages
                
        except Exception as e:
            logger.error(f"Error loading messages: {type(e).__name__}: {e}")
            return {}

    def save_messages(self, messages: Dict[str, Any]) -> bool:
        """Save messages to encrypted file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.messages_path), exist_ok=True)
            
            # Convert data to JSON and then to bytes
            data_json = json.dumps(messages, indent=2, sort_keys=True)
            data_bytes = data_json.encode('utf-8')
            
            # Use failsafe encryption for better reliability
            try:
                encrypted_data = encrypt_with_failsafe(data_bytes, client_ip='127.0.0.1')
            except CryptoException as e:
                logger.error(f"Failsafe encryption failed for messages: {e}")
                try:
                    encrypted_data = encrypt_data(data_bytes, client_ip='127.0.0.1')
                except CryptoException as fallback_error:
                    logger.error(f"All encryption methods failed for messages: {fallback_error}")
                    return False
            
            # Create backup of existing file before overwriting
            if self.messages_path.exists():
                backup_path = self.messages_path.with_suffix('.bak')
                try:
                    backup_path.write_bytes(self.messages_path.read_bytes())
                    logger.debug(f"Created backup at {backup_path}")
                except Exception as backup_error:
                    logger.warning(f"Could not create backup for messages: {backup_error}")
            
            # Write to temporary file first, then move to final location
            temp_path = self.messages_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'wb') as f:
                    f.write(encrypted_data)
                
                # Atomic move to final location
                temp_path.replace(self.messages_path)
                
                logger.info("Saved messages data successfully")
                return True
                
            except Exception as write_error:
                logger.error(f"Error writing encrypted messages data: {write_error}")
                # Clean up temp file if it exists
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
                return False
                
        except Exception as e:
            logger.error(f"Error saving messages data: {type(e).__name__}: {e}")
            return False