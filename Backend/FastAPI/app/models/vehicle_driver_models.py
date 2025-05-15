# app/models/vehicle_driver_models.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from enum import Enum
from datetime import date


class TransmissionType(str, Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"
    SEMI_AUTOMATIC = "Semi-Automatic"


class FuelType(str, Enum):
    DIESEL = "Diesel"
    GASOLINE = "Gasoline"
    ELECTRIC = "Electric"
    HYBRID = "Hybrid"
    CNG = "CNG"
    LPG = "LPG"


class GarageLocation(str, Enum):
    MAIN_DEPOT = "Main Depot"
    NORTH_DEPOT = "North Depot"
    SOUTH_DEPOT = "South Depot"
    EAST_DEPOT = "East Depot"
    WEST_DEPOT = "West Depot"


class VehicleStatus(str, Enum):
    ACTIVE = "Active"
    IN_MAINTENANCE = "In Maintenance"
    INACTIVE = "Inactive"


class Vehicle(BaseModel):
    id: Optional[str] = None
    vehicle_code: str
    license_plate: str
    brand: str
    model: str
    year: int = Field(..., ge=1900, le=2100)
    vin: str
    engine_type: str
    horsepower: int = Field(..., ge=0)
    transmission_type: TransmissionType
    fuel_type: FuelType
    fuel_tank_capacity_l: float = Field(..., ge=0)
    fuel_efficiency_kmpl: float = Field(..., ge=0)
    load_capacity_kg: float = Field(..., ge=0)
    number_of_axles: int = Field(..., ge=1)
    length_m: float = Field(..., ge=0)
    width_m: float = Field(..., ge=0)
    height_m: float = Field(..., ge=0)
    empty_weight_kg: float = Field(..., ge=0)
    assigned_garage: GarageLocation
    status: VehicleStatus
    purchase_date: Optional[date] = None
    purchase_price: float = Field(..., ge=0)
    notes: Optional[str] = None
    gps_tracking_enabled: Optional[bool] = False
    dash_camera_installed: Optional[bool] = False
    telematics_system_installed: Optional[bool] = False
    
    class Config:
        schema_extra = {
            "example": {
                "vehicle_code": "TRK-001",
                "license_plate": "ABC123",
                "brand": "Mercedes",
                "model": "Actros",
                "year": 2023,
                "vin": "WDBRR65J61A123456",
                "engine_type": "OM 471",
                "horsepower": 450,
                "transmission_type": "Automatic",
                "fuel_type": "Diesel",
                "fuel_tank_capacity_l": 650,
                "fuel_efficiency_kmpl": 3.2,
                "load_capacity_kg": 25000,
                "number_of_axles": 2,
                "length_m": 7.5,
                "width_m": 2.5,
                "height_m": 3.8,
                "empty_weight_kg": 7500,
                "assigned_garage": "Main Depot",
                "status": "Active",
                "purchase_price": 120000
            }
        }


class LicenseType(str, Enum):
    CDL_A = "CDL Class A"
    CDL_B = "CDL Class B"
    CDL_C = "CDL Class C"
    NON_CDL = "Non-CDL"


class EmploymentStatus(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    PROBATION = "Probation"


class Driver(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    address: str
    date_of_birth: date
    license_number: str
    license_type: LicenseType
    license_expiry_date: date
    issuing_state_country: str
    hire_date: date
    employee_id: str
    years_of_experience: float = Field(..., ge=0)
    employment_status: EmploymentStatus
    medical_information: Optional[str] = None
    emergency_contact: Optional[str] = None
    hazmat_endorsement: Optional[bool] = False
    tanker_endorsement: Optional[bool] = False
    passenger_endorsement: Optional[bool] = False
    
    class Config:
        schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone_number": "+1-555-123-4567",
                "address": "123 Main St, Anytown, USA",
                "date_of_birth": "1985-06-15",
                "license_number": "DL12345678",
                "license_type": "CDL Class A",
                "license_expiry_date": "2025-06-14",
                "issuing_state_country": "California",
                "hire_date": "2020-03-01",
                "employee_id": "EMP-001",
                "years_of_experience": 7.5,
                "employment_status": "Full-time"
            }
        }


class VehicleResponse(BaseModel):
    message: str
    vehicle: Optional[Vehicle] = None
    vehicles: Optional[List[Vehicle]] = None


class DriverResponse(BaseModel):
    message: str
    driver: Optional[Driver] = None
    drivers: Optional[List[Driver]] = None