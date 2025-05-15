# app/services/fleet_storage.py
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel

from app.services.crypto import encrypt_data, decrypt_data
from app.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FleetStorage:
    def __init__(self):
        """Initialize storage with the file paths"""
        self.data_dir = Path(settings.DATA_DIR)
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_user_vehicles_file(self, user_email: str) -> Path:
        """Get the path to a user's vehicles file"""
        # Use a hashed or sanitized version of the email to prevent directory traversal
        user_dir = self.data_dir / self._sanitize_email(user_email)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir / "vehicles.enc"
    
    def _get_user_drivers_file(self, user_email: str) -> Path:
        """Get the path to a user's drivers file"""
        # Use a hashed or sanitized version of the email to prevent directory traversal
        user_dir = self.data_dir / self._sanitize_email(user_email)
        os.makedirs(user_dir, exist_ok=True)
        return user_dir / "drivers.enc"
    
    def _sanitize_email(self, email: str) -> str:
        """Convert email to a safe directory name"""
        # Replace potentially problematic characters
        return email.replace("@", "_at_").replace(".", "_dot_")
    
    def _load_data(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """Load encrypted data from file
        
        Structure:
        {
            "item_id": {item_data},
            "item_id2": {item_data2},
        }
        """
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return {}
                    
                decrypted_data = decrypt_data(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return {}
    
    def _save_data(self, data: Dict[str, Any], file_path: Path) -> bool:
        """Save data to encrypted file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert data dict to JSON and then to bytes
            data_bytes = json.dumps(data).encode('utf-8')
            
            # Encrypt the data
            encrypted_data = encrypt_data(data_bytes)
            
            # Write to file
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
            return False
    
    # Vehicle operations
    def get_vehicles(self, user_email: str) -> List[Dict[str, Any]]:
        """Get all vehicles for a user"""
        file_path = self._get_user_vehicles_file(user_email)
        vehicles_data = self._load_data(file_path)
        return list(vehicles_data.values())
    
    def get_vehicle(self, user_email: str, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific vehicle by ID"""
        file_path = self._get_user_vehicles_file(user_email)
        vehicles_data = self._load_data(file_path)
        return vehicles_data.get(vehicle_id)
    
    def add_vehicle(self, user_email: str, vehicle_data: Dict[str, Any]) -> str:
        """Add a new vehicle for a user"""
        file_path = self._get_user_vehicles_file(user_email)
        vehicles_data = self._load_data(file_path)
        
        # Generate a unique ID if not provided
        vehicle_id = vehicle_data.get("id") or str(uuid.uuid4())
        vehicle_data["id"] = vehicle_id
        
        # Add creation timestamp
        vehicle_data["created_at"] = datetime.utcnow().isoformat()
        vehicle_data["created_by"] = user_email
        
        # Add vehicle
        vehicles_data[vehicle_id] = vehicle_data
        self._save_data(vehicles_data, file_path)
        
        # Log the operation
        logger.info(f"Vehicle added: {vehicle_id} for user {user_email}")
        
        return vehicle_id
    
    def update_vehicle(self, user_email: str, vehicle_id: str, vehicle_data: Dict[str, Any]) -> bool:
        """Update an existing vehicle"""
        file_path = self._get_user_vehicles_file(user_email)
        vehicles_data = self._load_data(file_path)
        
        if vehicle_id not in vehicles_data:
            logger.warning(f"Update failed: Vehicle {vehicle_id} not found for user {user_email}")
            return False
        
        # Keep the ID unchanged
        vehicle_data["id"] = vehicle_id
        
        # Preserve creation metadata
        if "created_at" in vehicles_data[vehicle_id]:
            vehicle_data["created_at"] = vehicles_data[vehicle_id]["created_at"]
        if "created_by" in vehicles_data[vehicle_id]:
            vehicle_data["created_by"] = vehicles_data[vehicle_id]["created_by"]
        
        # Add update metadata
        vehicle_data["updated_at"] = datetime.utcnow().isoformat()
        vehicle_data["updated_by"] = user_email
        
        # Update vehicle
        vehicles_data[vehicle_id] = vehicle_data
        success = self._save_data(vehicles_data, file_path)
        
        if success:
            logger.info(f"Vehicle updated: {vehicle_id} for user {user_email}")
        
        return success
    
    def delete_vehicle(self, user_email: str, vehicle_id: str) -> bool:
        """Delete a vehicle"""
        file_path = self._get_user_vehicles_file(user_email)
        vehicles_data = self._load_data(file_path)
        
        if vehicle_id not in vehicles_data:
            logger.warning(f"Delete failed: Vehicle {vehicle_id} not found for user {user_email}")
            return False
        
        # Delete vehicle
        del vehicles_data[vehicle_id]
        success = self._save_data(vehicles_data, file_path)
        
        if success:
            logger.info(f"Vehicle deleted: {vehicle_id} for user {user_email}")
        
        return success
    
    # Driver operations
    def get_drivers(self, user_email: str) -> List[Dict[str, Any]]:
        """Get all drivers for a user"""
        file_path = self._get_user_drivers_file(user_email)
        drivers_data = self._load_data(file_path)
        return list(drivers_data.values())
    
    def get_driver(self, user_email: str, driver_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific driver by ID"""
        file_path = self._get_user_drivers_file(user_email)
        drivers_data = self._load_data(file_path)
        return drivers_data.get(driver_id)
    
    def add_driver(self, user_email: str, driver_data: Dict[str, Any]) -> str:
        """Add a new driver for a user"""
        file_path = self._get_user_drivers_file(user_email)
        drivers_data = self._load_data(file_path)
        
        # Generate a unique ID if not provided
        driver_id = driver_data.get("id") or str(uuid.uuid4())
        driver_data["id"] = driver_id
        
        # Add creation metadata
        driver_data["created_at"] = datetime.utcnow().isoformat()
        driver_data["created_by"] = user_email
        
        # Add driver
        drivers_data[driver_id] = driver_data
        self._save_data(drivers_data, file_path)
        
        # Log the operation
        logger.info(f"Driver added: {driver_id} for user {user_email}")
        
        return driver_id
    
    def update_driver(self, user_email: str, driver_id: str, driver_data: Dict[str, Any]) -> bool:
        """Update an existing driver"""
        file_path = self._get_user_drivers_file(user_email)
        drivers_data = self._load_data(file_path)
        
        if driver_id not in drivers_data:
            logger.warning(f"Update failed: Driver {driver_id} not found for user {user_email}")
            return False
        
        # Keep the ID unchanged
        driver_data["id"] = driver_id
        
        # Preserve creation metadata
        if "created_at" in drivers_data[driver_id]:
            driver_data["created_at"] = drivers_data[driver_id]["created_at"]
        if "created_by" in drivers_data[driver_id]:
            driver_data["created_by"] = drivers_data[driver_id]["created_by"]
        
        # Add update metadata
        driver_data["updated_at"] = datetime.utcnow().isoformat()
        driver_data["updated_by"] = user_email
        
        # Update driver
        drivers_data[driver_id] = driver_data
        success = self._save_data(drivers_data, file_path)
        
        if success:
            logger.info(f"Driver updated: {driver_id} for user {user_email}")
        
        return success
    
    def delete_driver(self, user_email: str, driver_id: str) -> bool:
        """Delete a driver"""
        file_path = self._get_user_drivers_file(user_email)
        drivers_data = self._load_data(file_path)
        
        if driver_id not in drivers_data:
            logger.warning(f"Delete failed: Driver {driver_id} not found for user {user_email}")
            return False
        
        # Delete driver
        del drivers_data[driver_id]
        success = self._save_data(drivers_data, file_path)
        
        if success:
            logger.info(f"Driver deleted: {driver_id} for user {user_email}")
        
        return success