# app/services/storage.py
import os
import json
from pathlib import Path
from ..services.crypto import encrypt_data, decrypt_data
from ..config import settings

class UserStorage:
    def __init__(self):
        """Initialize storage with the file path from settings"""
        self.data_path = Path(settings.DATA_DIR) / settings.USER_DATA_FILE
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from encrypted file"""
        if not os.path.exists(self.data_path):
            return {}
        
        try:
            with open(self.data_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return {}
                    
                decrypted_data = decrypt_data(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            print(f"Error loading user data: {e}")
            return {}
    
    def _save_users(self):
        """Save users to encrypted file"""
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        # Convert users dict to JSON and then to bytes
        users_bytes = json.dumps(self.users).encode('utf-8')
        
        # Encrypt the data
        encrypted_data = encrypt_data(users_bytes)
        
        # Write to file
        with open(self.data_path, 'wb') as f:
            f.write(encrypted_data)
    
    def get_user_by_email(self, email: str):
        """Get a user by email"""
        return self.users.get(email)
    
    def save_user(self, user: dict):
        """Save a new user"""
        self.users[user["email"]] = user
        self._save_users()
    
    def update_user(self, user: dict):
        """Update an existing user"""
        if user["email"] in self.users:
            self.users[user["email"]] = user
            self._save_users()
            return True
        return False
    
    def delete_user(self, email: str):
        """Delete a user"""
        if email in self.users:
            del self.users[email]
            self._save_users()
            return True
        return False