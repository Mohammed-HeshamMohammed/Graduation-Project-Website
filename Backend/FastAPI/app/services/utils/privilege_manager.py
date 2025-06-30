import logging
from typing import List
from app.services.storage import UserStorage

logger = logging.getLogger(__name__)

class PrivilegeManager:
    HIERARCHY_ORDER = [
        "owner", "admin", "manager", "dispatcher",
        "engineer", "fuel_manager", "fleet_officer", "analyst", "viewer"
    ]

    def __init__(self, storage: UserStorage):
        self.storage = storage

    def has_privilege(self, user_privileges: List[str], required_privilege: str) -> bool:
        if not user_privileges or not isinstance(user_privileges, list):
            return False
        if required_privilege in user_privileges:
            return True
        user_level = self._get_highest_privilege_level(user_privileges)
        required_level = self._get_privilege_level(required_privilege)
        return user_level != -1 and required_level != -1 and user_level <= required_level

    def can_access_feature(self, user_privileges: List[str], feature: str) -> bool:
        if not user_privileges or not isinstance(user_privileges, list):
            return False
        feature_privileges = getattr(self.storage, 'PRIVILEGE_HIERARCHY', {}).get(feature, [])
        return any(priv in feature_privileges for priv in user_privileges)

    def get_user_privilege_level(self, user_privileges: List[str]) -> int:
        return self._get_highest_privilege_level(user_privileges)

    def is_higher_privilege(self, user_privileges: List[str], target_privileges: List[str]) -> bool:
        user_level = self._get_highest_privilege_level(user_privileges)
        target_level = self._get_highest_privilege_level(target_privileges)
        return user_level != -1 and target_level != -1 and user_level < target_level

    def can_manage_user(self, manager_privileges: List[str], target_privileges: List[str]) -> bool:
        if "owner" in manager_privileges:
            return "owner" not in target_privileges or manager_privileges == target_privileges
        if "admin" in manager_privileges:
            return not self._has_privilege_level(target_privileges, ["owner", "admin"])
        if "manager" in manager_privileges:
            return not self._has_privilege_level(target_privileges, ["owner", "admin", "manager"])
        return False

    def get_manageable_privileges(self, user_privileges: List[str]) -> List[str]:
        if "owner" in user_privileges:
            return [p for p in self.HIERARCHY_ORDER if p != "owner"]
        if "admin" in user_privileges:
            return [p for p in self.HIERARCHY_ORDER if p not in ["owner", "admin"]]
        if "manager" in user_privileges:
            return [p for p in self.HIERARCHY_ORDER if p not in ["owner", "admin", "manager"]]
        return []

    def _get_highest_privilege_level(self, privileges: List[str]) -> int:
        if not privileges or not isinstance(privileges, list):
            return -1
        for i, priv in enumerate(self.HIERARCHY_ORDER):
            if priv in privileges:
                return i
        return -1

    def _get_privilege_level(self, privilege: str) -> int:
        try:
            return self.HIERARCHY_ORDER.index(privilege)
        except ValueError:
            return -1

    def _has_privilege_level(self, privileges: List[str], check_privileges: List[str]) -> bool:
        if not privileges or not isinstance(privileges, list):
            return False
        return any(priv in privileges for priv in check_privileges)

    def get_privilege_hierarchy(self) -> List[str]:
        return self.HIERARCHY_ORDER.copy()

    def get_privilege_description(self, privilege: str) -> str:
        descriptions = {
            "owner": "Full system access and ownership",
            "admin": "Administrative access to all features",
            "manager": "Management access to team and operations",
            "dispatcher": "Dispatch and coordination operations",
            "engineer": "Technical and engineering operations",
            "fuel_manager": "Fuel management and monitoring",
            "fleet_officer": "Fleet operations and management",
            "analyst": "Data analysis and reporting",
            "viewer": "Read-only access to information"
        }
        return descriptions.get(privilege, f"Unknown privilege: {privilege}")

    def validate_privilege_assignment(self, assigner_privileges: List[str], target_privileges: List[str], new_privileges: List[str]) -> tuple[bool, str]:
        try:
            if not self.can_manage_user(assigner_privileges, target_privileges):
                return False, "Insufficient privileges to manage this user"
            manageable_privileges = self.get_manageable_privileges(assigner_privileges)
            for priv in new_privileges:
                if priv not in manageable_privileges and priv not in target_privileges:
                    return False, f"Cannot assign privilege: {priv}"
            return True, "Privilege assignment is valid"
        except Exception as e:
            logger.error(f"Error validating privilege assignment: {type(e).__name__}: {e}")
            return False, f"Validation error: {str(e)}"