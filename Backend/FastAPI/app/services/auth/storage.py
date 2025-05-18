# app/services/storage.py
import os
import json
from pathlib import Path
import logging
from app.services.crypto import encrypt_data, decrypt_data
from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class UserStorage:
    def __init__(self):
        """Initialize storage with the file path from settings"""
        self.data_dir = Path(settings.DATA_DIR)
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_path = self.data_dir / settings.USER_DATA_FILE
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from encrypted file"""
        if not os.path.exists(self.data_path):
            logger.info(f"User data file does not exist at {self.data_path}, creating new user store")
            return {}
        
        try:
            with open(self.data_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    logger.info("User data file exists but is empty")
                    return {}
                    
                decrypted_data = decrypt_data(encrypted_data)
                users = json.loads(decrypted_data.decode('utf-8'))
                logger.info(f"Loaded {len(users)} user(s) from storage")
                return users
        except FileNotFoundError:
            logger.warning(f"User data file not found at {self.data_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding user data JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading user data: {type(e).__name__}: {e}")
            return {}
    
    def _save_users(self):
        """Save users to encrypted file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            
            # Convert users dict to JSON and then to bytes
            users_bytes = json.dumps(self.users).encode('utf-8')
            
            # Encrypt the data
            encrypted_data = encrypt_data(users_bytes)
            
            # Write to file
            with open(self.data_path, 'wb') as f:
                f.write(encrypted_data)
                
            logger.info(f"Saved {len(self.users)} user(s) to storage")
            return True
        except Exception as e:
            logger.error(f"Error saving user data: {type(e).__name__}: {e}")
            return False
    
    def get_user_by_email(self, email: str):
        """Get a user by email"""
        user = self.users.get(email)
        return user
    
    def save_user(self, user: dict):
        """Save a new user"""
        try:
            self.users[user["email"]] = user
            success = self._save_users()
            return success
        except Exception as e:
            logger.error(f"Error saving user: {type(e).__name__}: {e}")
            return False
    
    def update_user(self, user: dict):
        """Update an existing user"""
        try:
            if user["email"] in self.users:
                self.users[user["email"]] = user
                success = self._save_users()
                return success
            logger.warning(f"Attempted to update non-existent user: {user['email']}")
            return False
        except Exception as e:
            logger.error(f"Error updating user: {type(e).__name__}: {e}")
            return False
    
    def delete_user(self, email: str):
        """Delete a user"""
        try:
            if email in self.users:
                del self.users[email]
                success = self._save_users()
                return success
            logger.warning(f"Attempted to delete non-existent user: {email}")
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {type(e).__name__}: {e}")
            return False