import logging

logger = logging.getLogger(__name__)

try:
    from .base_storage import BaseStorage
except ImportError as e:
    logger.error(f"Failed to import BaseStorage: {e}")
    raise

try:
    from .access_control import AccessControlMixin
except ImportError as e:
    logger.error(f"Failed to import AccessControlMixin: {e}")
    raise

try:
    from .file_handler import FileHandler, OperationResult
except ImportError as e:
    logger.error(f"Failed to import FileHandler or OperationResult: {e}")
    raise

try:
    from .user_storage import UserStorage
except ImportError as e:
    logger.error(f"Failed to import UserStorage: {e}")
    raise

try:
    from .company_file_handler import CompanyFileHandler
except ImportError as e:
    logger.error(f"Failed to import CompanyFileHandler: {e}")
    raise

try:
    from .company_storage import CompanyStorage
except ImportError as e:
    logger.error(f"Failed to import CompanyStorage: {e}")
    raise

__all__ = [
    'BaseStorage', 
    'AccessControlMixin',
    'FileHandler',
    'OperationResult',
    'UserStorage',
    'CompanyFileHandler',
    'CompanyStorage'
]

__version__ = '1.0.0'

def validate_imports():
    """Validate that all required components are properly imported."""
    required_components = {
        'BaseStorage': BaseStorage,
        'AccessControlMixin': AccessControlMixin,
        'FileHandler': FileHandler,
        'OperationResult': OperationResult,
        'UserStorage': UserStorage,
        'CompanyFileHandler': CompanyFileHandler,
        'CompanyStorage': CompanyStorage
    }
    
    missing_components = []
    for name, component in required_components.items():
        if component is None:
            missing_components.append(name)
    
    if missing_components:
        raise ImportError(f"Missing required components: {', '.join(missing_components)}")
    
    logger.info(f"All {len(required_components)} storage components validated successfully")
    return True

try:
    validate_imports()
    logger.info("Storage module initialization completed successfully")
except Exception as e:
    logger.error(f"Storage module validation failed: {e}")
    raise

def get_storage():
    """Get a UserStorage instance."""
    try:
        return UserStorage()
    except Exception as e:
        logger.error(f"Failed to initialize UserStorage: {e}")
        raise

def get_company_storage():
    """Get a CompanyStorage instance."""
    try:
        return CompanyStorage()
    except Exception as e:
        logger.error(f"Failed to initialize CompanyStorage: {e}")
        raise