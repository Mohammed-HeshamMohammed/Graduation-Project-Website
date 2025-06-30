from .service import MessagingService
from .storage import MessageStorage
from .access_control import MessageAccessControl
from .disciplinary import DisciplinaryActionManager
from .statistics import MessageStatistics
from .cleanup import MessageCleanup

messaging_service = MessagingService()

__all__ = [
    'MessagingService',
    'MessageStorage', 
    'MessageAccessControl',
    'DisciplinaryActionManager',
    'MessageStatistics',
    'MessageCleanup',
    'messaging_service'
]

__version__ = '1.2.0'