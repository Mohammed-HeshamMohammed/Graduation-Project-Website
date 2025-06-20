"""
Message Statistics Module

Handles message statistics and analytics functionality.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class MessageStatistics:
    """Handles message statistics and analytics"""
    
    def __init__(self, user_storage):
        """Initialize message statistics
        
        Args:
            user_storage: UserStorage instance
        """
        self.user_storage = user_storage
    
    def get_message_statistics(self, messages: Dict[str, List[Dict[str, Any]]], 
                             user_uuid: str = None, company_id: str = None) -> Dict[str, Any]:
        """Get message statistics
        
        Args:
            messages: Dictionary of user messages
            user_uuid: Optional specific user UUID for stats
            company_id: Optional company ID for stats
            
        Returns:
            Dictionary containing message statistics
        """
        try:
            stats = {
                'total_messages': 0,
                'unread_messages': 0,
                'message_types': {},
                'users_with_messages': 0
            }
            
            users_to_check = self._get_users_to_check(messages, user_uuid, company_id)
            stats['users_with_messages'] = len(users_to_check)
            
            for uuid in users_to_check:
                if uuid in messages:
                    for message in messages[uuid]:
                        stats['total_messages'] += 1
                        
                        if not message.get('read', False):
                            stats['unread_messages'] += 1
                        
                        msg_type = message.get('message_type', 'general')
                        stats['message_types'][msg_type] = stats['message_types'].get(msg_type, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting message statistics: {type(e).__name__}: {e}")
            return {}
    
    def get_user_statistics(self, messages: Dict[str, List[Dict[str, Any]]], 
                          user_uuid: str) -> Dict[str, Any]:
        """Get detailed statistics for a specific user
        
        Args:
            messages: Dictionary of user messages
            user_uuid: UUID of the user
            
        Returns:
            Dictionary containing user-specific statistics
        """
        try:
            if user_uuid not in messages:
                return {
                    'total_messages': 0,
                    'unread_messages': 0,
                    'message_types': {},
                    'recent_activity': []
                }
            
            user_messages = messages[user_uuid]
            stats = {
                'total_messages': len(user_messages),
                'unread_messages': 0,
                'message_types': {},
                'recent_activity': []
            }
            
            # Sort messages by timestamp for recent activity
            sorted_messages = sorted(user_messages, key=lambda x: x.get('timestamp', 0), reverse=True)
            
            for message in user_messages:
                if not message.get('read', False):
                    stats['unread_messages'] += 1
                
                msg_type = message.get('message_type', 'general')
                stats['message_types'][msg_type] = stats['message_types'].get(msg_type, 0) + 1
            
            # Get recent activity (last 10 messages)
            stats['recent_activity'] = [
                {
                    'id': msg.get('id'),
                    'type': msg.get('message_type', 'general'),
                    'timestamp': msg.get('timestamp'),
                    'created_at': msg.get('created_at'),
                    'read': msg.get('read', False)
                }
                for msg in sorted_messages[:10]
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {type(e).__name__}: {e}")
            return {}
    
    def get_company_statistics(self, messages: Dict[str, List[Dict[str, Any]]], 
                             company_id: str) -> Dict[str, Any]:
        """Get statistics for all users in a company
        
        Args:
            messages: Dictionary of user messages
            company_id: Company ID
            
        Returns:
            Dictionary containing company-wide statistics
        """
        try:
            company_users = self._get_company_users(company_id)
            
            stats = {
                'company_id': company_id,
                'total_users': len(company_users),
                'users_with_messages': 0,
                'total_messages': 0,
                'unread_messages': 0,
                'message_types': {},
                'user_breakdown': []
            }
            
            for user_uuid in company_users:
                user_stats = self.get_user_statistics(messages, user_uuid)
                
                if user_stats['total_messages'] > 0:
                    stats['users_with_messages'] += 1
                    stats['total_messages'] += user_stats['total_messages']
                    stats['unread_messages'] += user_stats['unread_messages']
                    
                    # Merge message types
                    for msg_type, count in user_stats['message_types'].items():
                        stats['message_types'][msg_type] = stats['message_types'].get(msg_type, 0) + count
                
                # Add user breakdown
                user_info = self.user_storage.get_user_by_uuid(user_uuid)
                stats['user_breakdown'].append({
                    'uuid': user_uuid,
                    'email': user_info.get('email', 'Unknown') if user_info else 'Unknown',
                    'full_name': user_info.get('full_name', 'Unknown') if user_info else 'Unknown',
                    'total_messages': user_stats['total_messages'],
                    'unread_messages': user_stats['unread_messages']
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting company statistics: {type(e).__name__}: {e}")
            return {}
    
    def get_system_wide_statistics(self, messages: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get system-wide message statistics
        
        Args:
            messages: Dictionary of user messages
            
        Returns:
            Dictionary containing system-wide statistics
        """
        try:
            stats = {
                'total_users_with_messages': len(messages),
                'total_messages': 0,
                'total_unread_messages': 0,
                'message_types': {},
                'companies': {},
                'top_message_types': [],
                'activity_summary': {
                    'disciplinary_actions': 0,
                    'warnings': 0,
                    'general_messages': 0,
                    'info_messages': 0
                }
            }
            
            # Process all messages
            for user_uuid, user_messages in messages.items():
                stats['total_messages'] += len(user_messages)
                
                for message in user_messages:
                    if not message.get('read', False):
                        stats['total_unread_messages'] += 1
                    
                    msg_type = message.get('message_type', 'general')
                    stats['message_types'][msg_type] = stats['message_types'].get(msg_type, 0) + 1
                    
                    # Activity summary
                    if msg_type == 'disciplinary':
                        stats['activity_summary']['disciplinary_actions'] += 1
                    elif msg_type == 'warning':
                        stats['activity_summary']['warnings'] += 1
                    elif msg_type == 'info':
                        stats['activity_summary']['info_messages'] += 1
                    else:
                        stats['activity_summary']['general_messages'] += 1
                
                # Company breakdown
                user_info = self.user_storage.get_user_by_uuid(user_uuid)
                if user_info:
                    company_id = user_info.get('company_id')
                    if company_id:
                        if company_id not in stats['companies']:
                            stats['companies'][company_id] = {
                                'users': 0,
                                'messages': 0,
                                'unread': 0
                            }
                        
                        stats['companies'][company_id]['users'] += 1
                        stats['companies'][company_id]['messages'] += len(user_messages)
                        stats['companies'][company_id]['unread'] += sum(
                            1 for msg in user_messages if not msg.get('read', False)
                        )
            
            # Sort message types by frequency
            stats['top_message_types'] = sorted(
                stats['message_types'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system-wide statistics: {type(e).__name__}: {e}")
            return {}
    
    def _get_users_to_check(self, messages: Dict[str, List[Dict[str, Any]]], 
                          user_uuid: str = None, company_id: str = None) -> List[str]:
        """Get list of user UUIDs to check for statistics"""
        if user_uuid:
            # Stats for specific user
            return [user_uuid] if user_uuid in messages else []
        elif company_id:
            # Stats for company users
            company_users = self._get_company_users(company_id)
            return [uuid for uuid in company_users if uuid in messages]
        else:
            # Global stats
            return list(messages.keys())
    
    def _get_company_users(self, company_id: str) -> List[str]:
        """Get all user UUIDs for a specific company"""
        company_users = []
        
        for email, user_data in self.user_storage.users.items():
            if (isinstance(user_data, dict) and 
                user_data.get('company_id') == company_id):
                company_users.append(user_data.get('uuid'))
        
        return company_users