# File: Password_History/utils/backup_utils.py
"""Backup utilities for password history"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from ..models.password_history import PasswordHistoryModel

logger = logging.getLogger(__name__)

class BackupUtils:
    """Utilities for backing up password history data"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / "backups"
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_automated_backup(self, model: PasswordHistoryModel) -> bool:
        """Create an automated backup with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"password_history_auto_{timestamp}.json"
            
            return self._save_backup(model, backup_file)
            
        except Exception as e:
            logger.error(f"Error creating automated backup: {e}")
            return False
    
    def create_manual_backup(self, model: PasswordHistoryModel, name: str = None) -> bool:
        """Create a manual backup with custom name"""
        try:
            if name:
                backup_file = self.backup_dir / f"password_history_manual_{name}.json"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"password_history_manual_{timestamp}.json"
            
            return self._save_backup(model, backup_file)
            
        except Exception as e:
            logger.error(f"Error creating manual backup: {e}")
            return False
    
    def _save_backup(self, model: PasswordHistoryModel, backup_path: Path) -> bool:
        """Save backup to specified path"""
        try:
            backup_data = {
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                'data': model.to_dict()
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2, sort_keys=True, default=str)
            
            logger.info(f"Backup created successfully at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving backup to {backup_path}: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("password_history_*.json"):
                try:
                    stat = backup_file.stat()
                    backups.append({
                        'filename': backup_file.name,
                        'path': str(backup_file),
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': 'auto' if 'auto_' in backup_file.name else 'manual'
                    })
                except Exception as e:
                    logger.warning(f"Error reading backup file {backup_file}: {e}")
                    continue
            
            # Sort by creation time, newest first
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def restore_from_backup(self, backup_filename: str) -> Optional[PasswordHistoryModel]:
        """Restore password history from backup"""
        try:
            backup_path = self.backup_dir / backup_filename
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_filename}")
                return None
            
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Validate backup structure
            if 'data' not in backup_data:
                logger.error(f"Invalid backup format in {backup_filename}")
                return None
            
            # Create and load model
            model = PasswordHistoryModel()
            model.from_dict(backup_data['data'])
            
            logger.info(f"Successfully restored from backup: {backup_filename}")
            return model
            
        except Exception as e:
            logger.error(f"Error restoring from backup {backup_filename}: {e}")
            return None
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backup files, keeping only the most recent ones"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                logger.info(f"Only {len(backups)} backups found, no cleanup needed")
                return 0
            
            # Remove oldest backups
            backups_to_remove = backups[keep_count:]
            removed_count = 0
            
            for backup in backups_to_remove:
                try:
                    backup_path = Path(backup['path'])
                    backup_path.unlink()
                    removed_count += 1
                    logger.debug(f"Removed old backup: {backup['filename']}")
                except Exception as e:
                    logger.warning(f"Failed to remove backup {backup['filename']}: {e}")
            
            logger.info(f"Cleaned up {removed_count} old backup files")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0

