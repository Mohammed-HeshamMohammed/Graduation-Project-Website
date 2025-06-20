"""
Message Cleanup Module

Handles cleanup and maintenance operations for messages.
"""

import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MessageCleanup:
    """Handles message cleanup and maintenance operations"""
    
    def __init__(self, save_messages_callback):
        """Initialize message cleanup
        
        Args:
            save_messages_callback: Callback function to save messages
        """
        self.save_messages = save_messages_callback
    
    def cleanup_old_messages(self, messages: Dict[str, List[Dict[str, Any]]], 
                           days_old: int = 90, user_uuid: str = None) -> int:
        """Clean up old messages
        
        Args:
            messages: Dictionary of user messages (will be modified in-place)
            days_old: Number of days old messages to clean up
            user_uuid: Optional specific user UUID to clean up
            
        Returns:
            Number of messages cleaned up
        """
        try:
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            users_to_clean = [user_uuid] if user_uuid else list(messages.keys())
            
            for uuid in users_to_clean:
                if uuid in messages:
                    original_count = len(messages[uuid])
                    messages[uuid] = [
                        msg for msg in messages[uuid]
                        if msg.get('timestamp', 0) > cutoff_time
                    ]
                    cleaned_count += original_count - len(messages[uuid])
                    
                    # Remove empty entries
                    if not messages[uuid]:
                        del messages[uuid]
            
            if cleaned_count > 0:
                self.save_messages(messages)
                logger.info(f"Cleaned {cleaned_count} old messages")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning old messages: {type(e).__name__}: {e}")
            return 0
    
    def cleanup_user_messages(self, messages: Dict[str, List[Dict[str, Any]]], 
                            user_uuid: str) -> bool:
        """Clean up messages for a deleted user
        
        Args:
            messages: Dictionary of user messages (will be modified in-place)
            user_uuid: UUID of the user to clean up
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_uuid in messages:
                del messages[user_uuid]
                success = self.save_messages(messages)
                
                if success:
                    logger.info(f"Cleaned up messages for deleted user: {user_uuid}")
                else:
                    logger.error(f"Failed to save after cleaning messages for user: {user_uuid}")
                
                return success
            
            return True  # No messages to clean up
            
        except Exception as e:
            logger.error(f"Error cleaning up user messages: {type(e).__name__}: {e}")
            return False
    
    def cleanup_messages_by_type(self, messages: Dict[str, List[Dict[str, Any]]], 
                               message_type: str, user_uuid: str = None) -> int:
        """Clean up messages of a specific type
        
        Args:
            messages: Dictionary of user messages (will be modified in-place)
            message_type: Type of messages to clean up
            user_uuid: Optional specific user UUID to clean up
            
        Returns:
            Number of messages cleaned up
        """
        try:
            cleaned_count = 0
            users_to_clean = [user_uuid] if user_uuid else list(messages.keys())
            
            for uuid in users_to_clean:
                if uuid in messages:
                    original_count = len(messages[uuid])
                    messages[uuid] = [
                        msg for msg in messages[uuid]
                        if msg.get('message_type') != message_type
                    ]
                    cleaned_count += original_count - len(messages[uuid])
                    
                    # Remove empty entries
                    if not messages[uuid]:
                        del messages[uuid]
            
            if cleaned_count > 0:
                self.save_messages(messages)
                logger.info(f"Cleaned {cleaned_count} messages of type '{message_type}'")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning messages by type: {type(e).__name__}: {e}")
            return 0
    
    def cleanup_read_messages(self, messages: Dict[str, List[Dict[str, Any]]], 
                            user_uuid: str = None, older_than_days: int = 30) -> int:
        """Clean up read messages older than specified days
        
        Args:
            messages: Dictionary of user messages (will be modified in-place)
            user_uuid: Optional specific user UUID to clean up
            older_than_days: Only clean read messages older than this many days
            
        Returns:
            Number of messages cleaned up
        """
        try:
            cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
            cleaned_count = 0
            
            users_to_clean = [user_uuid] if user_uuid else list(messages.keys())
            
            for uuid in users_to_clean:
                if uuid in messages:
                    original_count = len(messages[uuid])
                    messages[uuid] = [
                        msg for msg in messages[uuid]
                        if not (msg.get('read', False) and 
                               msg.get('timestamp', 0) < cutoff_time)
                    ]
                    cleaned_count += original_count - len(messages[uuid])
                    
                    # Remove empty entries
                    if not messages[uuid]:
                        del messages[uuid]
            
            if cleaned_count > 0:
                self.save_messages(messages)
                logger.info(f"Cleaned {cleaned_count} read messages older than {older_than_days} days")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning read messages: {type(e).__name__}: {e}")
            return 0
    
    def optimize_message_storage(self, messages: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Optimize message storage by removing duplicates and organizing data
        
        Args:
            messages: Dictionary of user messages (will be modified in-place)
            
        Returns:
            Dictionary with optimization results
        """
        try:
            stats = {
                'duplicates_removed': 0,
                'users_processed': 0,
                'empty_users_removed': 0
            }
            
            users_to_remove = []
            
            for user_uuid, user_messages in messages.items():
                stats['users_processed'] += 1
                
                if not user_messages:
                    users_to_remove.append(user_uuid)
                    continue
                
                # Remove duplicates based on message ID
                seen_ids = set()
                unique_messages = []
                
                for message in user_messages:
                    msg_id = message.get('id')
                    if msg_id and msg_id not in seen_ids:
                        seen_ids.add(msg_id)
                        unique_messages.append(message)
                    elif msg_id:
                        stats['duplicates_removed'] += 1
                    else:
                        # Message without ID, keep it but assign a new ID
                        unique_messages.append(message)
                
                # Sort messages by timestamp
                unique_messages.sort(key=lambda x: x.get('timestamp', 0))
                messages[user_uuid] = unique_messages
            
            # Remove empty user entries
            for user_uuid in users_to_remove:
                del messages[user_uuid]
                stats['empty_users_removed'] += 1
            
            if stats['duplicates_removed'] > 0 or stats['empty_users_removed'] > 0:
                self.save_messages(messages)
                logger.info(f"Optimized messages: removed {stats['duplicates_removed']} duplicates and {stats['empty_users_removed']} empty user entries")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error optimizing message storage: {type(e).__name__}: {e}")
            return {'error': str(e)}
    
    def archive_old_messages(self, messages: Dict[str, List[Dict[str, Any]]], 
                           days_old: int = 365, archive_path: str = None) -> Dict[str, Any]:
        """Archive old messages to a separate file (placeholder for future implementation)
        
        Args:
            messages: Dictionary of user messages
            days_old: Age threshold for archiving
            archive_path: Optional path for archive file
            
        Returns:
            Dictionary with archiving results
        """
        try:
            # This is a placeholder for future archiving functionality
            # For now, just return statistics about what would be archived
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            
            stats = {
                'messages_to_archive': 0,
                'users_affected': 0,
                'total_size_estimate': 0
            }
            
            for user_uuid, user_messages in messages.items():
                old_messages = [
                    msg for msg in user_messages
                    if msg.get('timestamp', 0) < cutoff_time
                ]
                
                if old_messages:
                    stats['messages_to_archive'] += len(old_messages)
                    stats['users_affected'] += 1
                    
                    # Rough size estimate (assuming average 200 bytes per message)
                    stats['total_size_estimate'] += len(old_messages) * 200
            
            logger.info(f"Archive analysis: {stats['messages_to_archive']} messages from {stats['users_affected']} users could be archived")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing messages for archiving: {type(e).__name__}: {e}")
            return {'error': str(e)}