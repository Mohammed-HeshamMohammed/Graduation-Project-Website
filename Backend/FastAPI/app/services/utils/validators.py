import logging
from typing import Set

logger = logging.getLogger(__name__)

class UserValidator:
    VALID_PRIVILEGES: Set[str] = {
        'owner', 'admin', 'add', 'remove', 'manager', 'dispatcher',
        'engineer', 'fuel_manager', 'fleet_officer', 'analyst', 'viewer'
    }
    REQUIRED_FIELDS = ['uuid', 'email', 'password', 'full_name', 'company_id']
    BOOLEAN_FIELDS = ['verified', 'is_logged_in', 'is_owner']

    def validate_user_data(self, user_data: dict) -> tuple[bool, str]:
        if not isinstance(user_data, dict):
            return False, "User data must be a dictionary"
        for field in self.REQUIRED_FIELDS:
            if field not in user_data:
                return False, f"Missing required field: {field}"
        if not self.validate_uuid_format(user_data.get('uuid')):
            return False, "Invalid UUID"
        if not self.validate_email_format(user_data.get('email')):
            return False, "Invalid email format"
        if not isinstance(user_data.get('full_name'), str) or not user_data['full_name'].strip():
            return False, "Invalid full name"
        if not self.validate_company_id(user_data.get('company_id')):
            return False, "Invalid company ID"
        if not isinstance(user_data.get('password'), str) or not user_data['password']:
            return False, "Invalid password"
        for field in self.BOOLEAN_FIELDS:
            if field in user_data and not isinstance(user_data[field], bool):
                return False, f"Field {field} must be boolean"
        privileges = user_data.get('privileges')
        if privileges is not None:
            if not isinstance(privileges, list):
                return False, "Privileges must be a list"
            for priv in privileges:
                if not self.is_valid_privilege(priv):
                    return False, f"Invalid privilege: {priv}"
        return True, "Valid user data"

    def validate_email_format(self, email: str) -> bool:
        if not isinstance(email, str):
            return False
        email = email.strip()
        if not email or '@' not in email:
            return False
        local, _, domain = email.partition('@')
        return bool(local and domain and '.' in domain)

    def validate_uuid_format(self, uuid: str) -> bool:
        return isinstance(uuid, str) and bool(uuid.strip())

    def validate_company_id(self, company_id: str) -> bool:
        return isinstance(company_id, str) and bool(company_id.strip())

    def get_valid_privileges(self) -> Set[str]:
        return self.VALID_PRIVILEGES.copy()

    def is_valid_privilege(self, privilege: str) -> bool:
        return isinstance(privilege, str) and privilege in self.VALID_PRIVILEGES