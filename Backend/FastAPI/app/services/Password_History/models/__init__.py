# File: app/services/Password_History/models/__init__.py
"""Password History Models"""
# File: Password_History/models/__init__.py
"""Password History Models

This module provides classes for managing password history data structures.

USAGE EXAMPLES:
    from Password_History.models import PasswordHistoryModel, PasswordHistoryEntry
    
    # Create a password history manager
    history_model = PasswordHistoryModel()
    
    # Add a password entry
    success = history_model.add_entry(
        user_uuid="user123",
        company_uuid="company456", 
        password_hash="hashed_password",
        max_history=5
    )

CLASSES AVAILABLE:
    - PasswordHistoryModel: Main class for managing password histories
    - PasswordHistoryEntry: Individual password history record
"""

from .password_history import PasswordHistoryModel, PasswordHistoryEntry

__all__ = ["PasswordHistoryModel", "PasswordHistoryEntry"]

# ============================================================================
# PASSWORDHISTORYMODEL - Main Functions Documentation
# ============================================================================

"""
PasswordHistoryModel() -> PasswordHistoryModel
    Creates a new password history manager instance.
    
    SENDS: Nothing (constructor)
    RECEIVES: PasswordHistoryModel instance
    
    EXAMPLE:
        history = PasswordHistoryModel()

---

add_entry(user_uuid: str, company_uuid: str, password_hash: str, max_history: int = 5) -> bool
    Adds a new password to user's history.
    
    SENDS:
        - user_uuid: String identifier for the user
        - company_uuid: String identifier for the company
        - password_hash: Hashed password string
        - max_history: Maximum number of passwords to keep (default: 5)
    
    RECEIVES:
        - bool: True if password was added, False if it's duplicate of last password
    
    EXAMPLE:
        success = history.add_entry("user123", "company456", "hash123", 10)
        if success:
            print("Password added to history")

---

check_password_exists(user_uuid: str, password_hash: str) -> bool
    Checks if a password already exists in user's history.
    
    SENDS:
        - user_uuid: String identifier for the user
        - password_hash: Hashed password to check
    
    RECEIVES:
        - bool: True if password exists in history, False otherwise
    
    EXAMPLE:
        exists = history.check_password_exists("user123", "hash123")
        if exists:
            print("Password was used before!")

---

get_company_histories(company_uuid: str) -> Dict[str, List[PasswordHistoryEntry]]
    Gets all password histories for users in a specific company.
    
    SENDS:
        - company_uuid: String identifier for the company
    
    RECEIVES:
        - Dict: Keys are user_uuids, values are lists of PasswordHistoryEntry objects
    
    EXAMPLE:
        company_data = history.get_company_histories("company456")
        for user_id, entries in company_data.items():
            print(f"User {user_id} has {len(entries)} passwords")

---

clear_user_history(user_uuid: str) -> None
    Removes all password history for a specific user.
    
    SENDS:
        - user_uuid: String identifier for the user
    
    RECEIVES:
        - None (void function)
    
    EXAMPLE:
        history.clear_user_history("user123")
        print("User history cleared")

---

get_user_history_count(user_uuid: str) -> int
    Gets the number of passwords stored for a user.
    
    SENDS:
        - user_uuid: String identifier for the user
    
    RECEIVES:
        - int: Number of passwords in user's history (0 if user not found)
    
    EXAMPLE:
        count = history.get_user_history_count("user123")
        print(f"User has {count} passwords in history")

---

cleanup_orphaned_histories(valid_user_uuids: set) -> int
    Removes histories for users that no longer exist.
    
    SENDS:
        - valid_user_uuids: Set of strings containing current valid user IDs
    
    RECEIVES:
        - int: Number of orphaned histories that were removed
    
    EXAMPLE:
        active_users = {"user123", "user456", "user789"}
        removed = history.cleanup_orphaned_histories(active_users)
        print(f"Removed {removed} orphaned histories")

---

to_dict() -> Dict
    Converts the entire model to a dictionary for serialization/storage.
    
    SENDS: Nothing
    
    RECEIVES:
        - Dict: Structure is {user_uuid: [list of entry dictionaries]}
        - Each entry dict contains: password_hash, created_at, company_uuid, user_uuid
    
    EXAMPLE:
        data = history.to_dict()
        json.dump(data, open('backup.json', 'w'))

---

from_dict(data: Dict) -> None
    Loads the model from a dictionary (for deserialization).
    
    SENDS:
        - data: Dict with structure {user_uuid: [list of entry dictionaries]}
    
    RECEIVES:
        - None (void function, modifies the instance)
    
    EXAMPLE:
        data = json.load(open('backup.json', 'r'))
        history.from_dict(data)

---

get_statistics() -> Dict
    Gets comprehensive statistics about the password histories.
    
    SENDS: Nothing
    
    RECEIVES:
        - Dict containing:
            * total_users_with_history: int
            * total_passwords_stored: int  
            * average_passwords_per_user: float
            * users_by_history_count: Dict[int, int] (history_size -> user_count)
            * companies: Dict[company_uuid, {unique_users: int, total_passwords: int}]
    
    EXAMPLE:
        stats = history.get_statistics()
        print(f"Total users: {stats['total_users_with_history']}")
        print(f"Average passwords per user: {stats['average_passwords_per_user']}")
"""

# ============================================================================
# PASSWORDHISTORYENTRY - Individual Record Documentation  
# ============================================================================

"""
PasswordHistoryEntry(password_hash: str, created_at: datetime, company_uuid: str, user_uuid: str)
    Creates an individual password history record.
    
    SENDS:
        - password_hash: Hashed password string
        - created_at: datetime object when password was created
        - company_uuid: String identifier for company
        - user_uuid: String identifier for user
    
    RECEIVES: PasswordHistoryEntry instance
    
    EXAMPLE:
        from datetime import datetime
        entry = PasswordHistoryEntry(
            password_hash="hash123",
            created_at=datetime.now(),
            company_uuid="company456", 
            user_uuid="user123"
        )

---

to_dict() -> Dict
    Converts entry to dictionary format.
    
    SENDS: Nothing
    
    RECEIVES:
        - Dict with keys: password_hash, created_at (ISO format), company_uuid, user_uuid
    
    EXAMPLE:
        entry_dict = entry.to_dict()
        # Result: {'password_hash': 'hash123', 'created_at': '2024-01-15T10:30:00', ...}

---

from_dict(data: Dict) -> PasswordHistoryEntry (class method)
    Creates entry from dictionary.
    
    SENDS:
        - data: Dict with keys: password_hash, created_at, company_uuid, user_uuid
    
    RECEIVES:
        - PasswordHistoryEntry: New instance created from the data
    
    EXAMPLE:
        data = {'password_hash': 'hash123', 'created_at': '2024-01-15T10:30:00', 
                'company_uuid': 'company456', 'user_uuid': 'user123'}
        entry = PasswordHistoryEntry.from_dict(data)
"""

from .password_history import PasswordHistoryModel, PasswordHistoryEntry

__all__ = ["PasswordHistoryModel", "PasswordHistoryEntry"]