# app/routes/fleet.py
from fastapi import APIRouter, HTTPException, Query, status, Depends
from datetime import datetime
import logging
import uuid
from typing import List, Optional, Dict, Any

from app.models.vehicle_driver_models import (
    Vehicle, 
    Driver, 
    VehicleResponse, 
    DriverResponse
)
from app.services.fleet_storage import FleetStorage
from app.services.utils import verify_token
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
fleet_storage = FleetStorage()

# Authentication dependency
async def get_current_user(token: str = Query(...)) -> str:
    """Dependency to get current authenticated user email"""
    payload = verify_token(token)
    
    # Check for token errors
    if "error" in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {payload['error']}"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    return email

# Vehicle routes
@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(vehicle: Vehicle, user_email: str = Depends(get_current_user)):
    """Create a new vehicle"""
    try:
        # Convert Pydantic model to dict and handle date fields
        vehicle_data = vehicle.dict()
        if vehicle_data.get("purchase_date"):
            vehicle_data["purchase_date"] = vehicle_data["purchase_date"].isoformat()
        
        # Add vehicle
        vehicle_id = fleet_storage.add_vehicle(user_email, vehicle_data)
        
        # Update ID in vehicle data
        vehicle_data["id"] = vehicle_id
        
        logger.info(f"Vehicle created: {vehicle_id} for user {user_email}")
        
        return {
            "message": "Vehicle created successfully",
            "vehicle": Vehicle(**vehicle_data)
        }
    except Exception as e:
        logger.error(f"Error creating vehicle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the vehicle: {str(e)}"
        )

@router.get("/vehicles", response_model=VehicleResponse)
async def get_vehicles(user_email: str = Depends(get_current_user)):
    """Get all vehicles for the user"""
    try:
        vehicles_data = fleet_storage.get_vehicles(user_email)
        
        # Convert dates from ISO strings back to date objects for Pydantic model
        vehicles = []
        for v in vehicles_data:
            if isinstance(v.get("purchase_date"), str):
                try:
                    v["purchase_date"] = datetime.fromisoformat(v["purchase_date"]).date()
                except ValueError:
                    v["purchase_date"] = None
            vehicles.append(Vehicle(**v))
        
        return {
            "message": f"Retrieved {len(vehicles)} vehicles",
            "vehicles": vehicles
        }
    except Exception as e:
        logger.error(f"Error retrieving vehicles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving vehicles: {str(e)}"
        )

@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: str, user_email: str = Depends(get_current_user)):
    """Get a specific vehicle by ID"""
    try:
        vehicle_data = fleet_storage.get_vehicle(user_email, vehicle_id)
        
        if not vehicle_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Convert dates from ISO strings back to date objects for Pydantic model
        if isinstance(vehicle_data.get("purchase_date"), str):
            try:
                vehicle_data["purchase_date"] = datetime.fromisoformat(vehicle_data["purchase_date"]).date()
            except ValueError:
                vehicle_data["purchase_date"] = None
        
        return {
            "message": "Vehicle retrieved successfully",
            "vehicle": Vehicle(**vehicle_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vehicle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the vehicle: {str(e)}"
        )

@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(vehicle_id: str, vehicle: Vehicle, user_email: str = Depends(get_current_user)):
    """Update a vehicle"""
    try:
        # Check if vehicle exists
        existing_vehicle = fleet_storage.get_vehicle(user_email, vehicle_id)
        if not existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Convert Pydantic model to dict and handle date fields
        vehicle_data = vehicle.dict()
        if vehicle_data.get("purchase_date"):
            vehicle_data["purchase_date"] = vehicle_data["purchase_date"].isoformat()
        
        # Update vehicle
        success = fleet_storage.update_vehicle(user_email, vehicle_id, vehicle_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update vehicle"
            )
        
        # Convert dates back for response
        if isinstance(vehicle_data.get("purchase_date"), str):
            try:
                vehicle_data["purchase_date"] = datetime.fromisoformat(vehicle_data["purchase_date"]).date()
            except ValueError:
                vehicle_data["purchase_date"] = None
                
        logger.info(f"Vehicle updated: {vehicle_id} for user {user_email}")
        
        return {
            "message": "Vehicle updated successfully",
            "vehicle": Vehicle(**vehicle_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vehicle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the vehicle: {str(e)}"
        )

@router.delete("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def delete_vehicle(vehicle_id: str, user_email: str = Depends(get_current_user)):
    """Delete a vehicle"""
    try:
        # Check if vehicle exists
        existing_vehicle = fleet_storage.get_vehicle(user_email, vehicle_id)
        if not existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Delete vehicle
        success = fleet_storage.delete_vehicle(user_email, vehicle_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete vehicle"
            )
        
        logger.info(f"Vehicle deleted: {vehicle_id} for user {user_email}")
        
        return {
            "message": "Vehicle deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the vehicle: {str(e)}"
        )

# Driver routes
@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(driver: Driver, user_email: str = Depends(get_current_user)):
    """Create a new driver"""
    try:
        # Convert Pydantic model to dict and handle date fields
        driver_data = driver.dict()
        if driver_data.get("date_of_birth"):
            driver_data["date_of_birth"] = driver_data["date_of_birth"].isoformat()
        if driver_data.get("license_expiry_date"):
            driver_data["license_expiry_date"] = driver_data["license_expiry_date"].isoformat()
        if driver_data.get("hire_date"):
            driver_data["hire_date"] = driver_data["hire_date"].isoformat()
        
        # Add driver
        driver_id = fleet_storage.add_driver(user_email, driver_data)
        
        # Update ID in driver data
        driver_data["id"] = driver_id
        
        logger.info(f"Driver created: {driver_id} for user {user_email}")
        
        return {
            "message": "Driver created successfully",
            "driver": Driver(**driver_data)
        }
    except Exception as e:
        logger.error(f"Error creating driver: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the driver: {str(e)}"
        )

@router.get("/drivers", response_model=DriverResponse)
async def get_drivers(user_email: str = Depends(get_current_user)):
    """Get all drivers for the user"""
    try:
        drivers_data = fleet_storage.get_drivers(user_email)
        
        # Convert dates from ISO strings back to date objects for Pydantic model
        drivers = []
        for d in drivers_data:
            for date_field in ["date_of_birth", "license_expiry_date", "hire_date"]:
                if isinstance(d.get(date_field), str):
                    try:
                        d[date_field] = datetime.fromisoformat(d[date_field]).date()
                    except ValueError:
                        d[date_field] = None
            drivers.append(Driver(**d))
        
        return {
            "message": f"Retrieved {len(drivers)} drivers",
            "drivers": drivers
        }
    except Exception as e:
        logger.error(f"Error retrieving drivers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving drivers: {str(e)}"
        )

@router.get("/drivers/{driver_id}", response_model=DriverResponse)
async def get_driver(driver_id: str, user_email: str = Depends(get_current_user)):
    """Get a specific driver by ID"""
    try:
        driver_data = fleet_storage.get_driver(user_email, driver_id)
        
        if not driver_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Convert dates from ISO strings back to date objects for Pydantic model
        for date_field in ["date_of_birth", "license_expiry_date", "hire_date"]:
            if isinstance(driver_data.get(date_field), str):
                try:
                    driver_data[date_field] = datetime.fromisoformat(driver_data[date_field]).date()
                except ValueError:
                    driver_data[date_field] = None
        
        return {
            "message": "Driver retrieved successfully",
            "driver": Driver(**driver_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving driver: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the driver: {str(e)}"
        )

@router.put("/drivers/{driver_id}", response_model=DriverResponse)
async def update_driver(driver_id: str, driver: Driver, user_email: str = Depends(get_current_user)):
    """Update a driver"""
    try:
        # Check if driver exists
        existing_driver = fleet_storage.get_driver(user_email, driver_id)
        if not existing_driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Convert Pydantic model to dict and handle date fields
        driver_data = driver.dict()
        if driver_data.get("date_of_birth"):
            driver_data["date_of_birth"] = driver_data["date_of_birth"].isoformat()
        if driver_data.get("license_expiry_date"):
            driver_data["license_expiry_date"] = driver_data["license_expiry_date"].isoformat()
        if driver_data.get("hire_date"):
            driver_data["hire_date"] = driver_data["hire_date"].isoformat()
        
        # Update driver
        success = fleet_storage.update_driver(user_email, driver_id, driver_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update driver"
            )
        
        # Convert dates back for response
        for date_field in ["date_of_birth", "license_expiry_date", "hire_date"]:
            if isinstance(driver_data.get(date_field), str):
                try:
                    driver_data[date_field] = datetime.fromisoformat(driver_data[date_field]).date()
                except ValueError:
                    driver_data[date_field] = None
                
        logger.info(f"Driver updated: {driver_id} for user {user_email}")
        
        return {
            "message": "Driver updated successfully",
            "driver": Driver(**driver_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating driver: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the driver: {str(e)}"
        )

@router.delete("/drivers/{driver_id}", response_model=DriverResponse)
async def delete_driver(driver_id: str, user_email: str = Depends(get_current_user)):
    """Delete a driver"""
    try:
        # Check if driver exists
        existing_driver = fleet_storage.get_driver(user_email, driver_id)
        if not existing_driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Delete driver
        success = fleet_storage.delete_driver(user_email, driver_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete driver"
            )
        
        logger.info(f"Driver deleted: {driver_id} for user {user_email}")
        
        return {
            "message": "Driver deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting driver: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the driver: {str(e)}"
        )