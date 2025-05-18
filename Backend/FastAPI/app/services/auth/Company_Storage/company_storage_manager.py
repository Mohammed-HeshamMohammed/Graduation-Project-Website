# app/services/auth/Company_Storage/company_storage_manager.py
import os
import json
import logging
from pathlib import Path
from app.services.crypto import encrypt_data, decrypt_data

# Configure logging
logger = logging.getLogger(__name__)

class CompanyStorageManager:
    def __init__(self, data_dir: Path, data_file: str = "company_data.json"):
        """
        Initialize storage manager with the file path
        
        Args:
            data_dir: Directory path for data storage
            data_file: Filename for company data
        """
        self.data_dir = data_dir
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_path = self.data_dir / data_file
    
    def load_companies(self):
        """
        Load companies from encrypted file
        
        Returns:
            dict: Dictionary of companies
        """
        if not os.path.exists(self.data_path):
            logger.info(f"Company data file does not exist at {self.data_path}, creating new company store")
            return {}
        
        try:
            with open(self.data_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    logger.info("Company data file exists but is empty")
                    return {}
                    
                decrypted_data = decrypt_data(encrypted_data)
                companies = json.loads(decrypted_data.decode('utf-8'))
                logger.info(f"Loaded {len(companies)} companies from storage")
                return companies
        except FileNotFoundError:
            logger.warning(f"Company data file not found at {self.data_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding company data JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading company data: {type(e).__name__}: {e}")
            return {}
    
    def save_companies(self, companies):
        """
        Save companies to encrypted file
        
        Args:
            companies: Dictionary of companies to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            
            # Convert companies dict to JSON and then to bytes
            companies_bytes = json.dumps(companies).encode('utf-8')
            
            # Encrypt the data
            encrypted_data = encrypt_data(companies_bytes)
            
            # Write to file
            with open(self.data_path, 'wb') as f:
                f.write(encrypted_data)
                
            logger.info(f"Saved {len(companies)} companies to storage")
            return True
        except Exception as e:
            logger.error(f"Error saving company data: {type(e).__name__}: {e}")
            return False