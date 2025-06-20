# File: Password_History/models/password_history.py
"""Password history data models"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class PasswordHistoryEntry:
    """Individual password history entry"""
    password_hash: str
    created_at: datetime
    company_uuid: str
    user_uuid: str
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary"""
        return {
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat(),
            'company_uuid': self.company_uuid,
            'user_uuid': self.user_uuid
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PasswordHistoryEntry':
        """Create entry from dictionary"""
        return cls(
            password_hash=data['password_hash'],
            created_at=datetime.fromisoformat(data['created_at']),
            company_uuid=data['company_uuid'],
            user_uuid=data['user_uuid']
        )

class PasswordHistoryModel:
    """Model for managing password history data structure"""
    
    def __init__(self):
        self.histories: Dict[str, List[PasswordHistoryEntry]] = {}
    
    def add_entry(self, user_uuid: str, company_uuid: str, password_hash: str, max_history: int = 5):
        """Add a password entry to user's history"""
        if user_uuid not in self.histories:
            self.histories[user_uuid] = []
        
        entry = PasswordHistoryEntry(
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            company_uuid=company_uuid,
            user_uuid=user_uuid
        )
        
        # Don't add if it's the same as the last password
        history = self.histories[user_uuid]
        if history and history[-1].password_hash == password_hash:
            return False
        
        history.append(entry)
        
        # Keep only the last max_history passwords
        if len(history) > max_history:
            self.histories[user_uuid] = history[-max_history:]
        
        return True
    
    def check_password_exists(self, user_uuid: str, password_hash: str) -> bool:
        """Check if password exists in user's history"""
        if user_uuid not in self.histories:
            return False
        
        return any(entry.password_hash == password_hash 
                  for entry in self.histories[user_uuid])
    
    def get_company_histories(self, company_uuid: str) -> Dict[str, List[PasswordHistoryEntry]]:
        """Get all password histories for users in a company"""
        company_histories = {}
        
        for user_uuid, entries in self.histories.items():
            # Filter entries that belong to the specified company
            company_entries = [entry for entry in entries 
                             if entry.company_uuid == company_uuid]
            
            if company_entries:
                company_histories[user_uuid] = company_entries
        
        return company_histories
    
    def clear_user_history(self, user_uuid: str):
        """Clear history for a specific user"""
        if user_uuid in self.histories:
            del self.histories[user_uuid]
    
    def get_user_history_count(self, user_uuid: str) -> int:
        """Get count of passwords in user's history"""
        return len(self.histories.get(user_uuid, []))
    
    def cleanup_orphaned_histories(self, valid_user_uuids: set):
        """Remove histories for users that no longer exist"""
        orphaned_uuids = set(self.histories.keys()) - valid_user_uuids
        
        for uuid in orphaned_uuids:
            del self.histories[uuid]
        
        return len(orphaned_uuids)
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary for serialization"""
        return {
            user_uuid: [entry.to_dict() for entry in entries]
            for user_uuid, entries in self.histories.items()
        }
    
    def from_dict(self, data: Dict):
        """Load model from dictionary"""
        self.histories = {}
        
        for user_uuid, entries_data in data.items():
            self.histories[user_uuid] = [
                PasswordHistoryEntry.from_dict(entry_data)
                for entry_data in entries_data
            ]
    
    def get_statistics(self) -> Dict:
        """Get statistics about password histories"""
        total_users = len(self.histories)
        total_passwords = sum(len(entries) for entries in self.histories.values())
        
        stats = {
            'total_users_with_history': total_users,
            'total_passwords_stored': total_passwords,
            'average_passwords_per_user': round(total_passwords / total_users, 2) if total_users > 0 else 0,
            'users_by_history_count': {},
            'companies': {}
        }
        
        # Count users by number of passwords in history
        for entries in self.histories.values():
            count = len(entries)
            stats['users_by_history_count'][count] = stats['users_by_history_count'].get(count, 0) + 1
        
        # Company statistics
        company_stats = {}
        for user_uuid, entries in self.histories.items():
            for entry in entries:
                company_uuid = entry.company_uuid
                if company_uuid not in company_stats:
                    company_stats[company_uuid] = {'users': set(), 'passwords': 0}
                
                company_stats[company_uuid]['users'].add(user_uuid)
                company_stats[company_uuid]['passwords'] += 1
        
        # Convert sets to counts
        for company_uuid, data in company_stats.items():
            stats['companies'][company_uuid] = {
                'unique_users': len(data['users']),
                'total_passwords': data['passwords']
            }
        
        return stats