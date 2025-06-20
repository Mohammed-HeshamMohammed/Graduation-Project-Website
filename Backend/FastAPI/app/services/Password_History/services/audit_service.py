# File: Password_History/services/audit_service.py
"""Audit service for comprehensive logging of password history operations"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class AuditEntry:
    """Audit log entry"""
    timestamp: datetime
    operation_id: str
    operation_type: str
    user_uuid: str
    company_uuid: str
    requesting_user_uuid: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    error_message: Optional[str]
    duration_ms: Optional[float]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AuditEntry':
        """Create from dictionary"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class AuditService:
    """Service for audit logging and compliance"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.audit_dir = self.data_dir / "audit_logs"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        self._lock = threading.RLock()
        self._buffer = []
        self._buffer_size = 100
        self._last_flush = time.time()
        self._flush_interval = 60  # seconds
        
        # Operation tracking
        self._active_operations = {}
        self._operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'average_duration': 0.0,
            'operations_by_type': {}
        }
        
        # Start background flush thread
        self._flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self._flush_thread.start()
        
        logger.info(f"Audit service initialized with log directory: {self.audit_dir}")
    
    def log_operation_start(self, 
                          operation_id: str,
                          operation_type: str,
                          user_uuid: str = None,
                          company_uuid: str = None,
                          requesting_user_uuid: str = None,
                          ip_address: str = None,
                          user_agent: str = None,
                          metadata: Dict = None):
        """Log the start of an operation"""
        with self._lock:
            self._active_operations[operation_id] = {
                'start_time': time.time(),
                'operation_type': operation_type,
                'user_uuid': user_uuid,
                'company_uuid': company_uuid,
                'requesting_user_uuid': requesting_user_uuid,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'metadata': metadata or {}
            }
    
    def log_operation_success(self, operation_id: str, additional_metadata: Dict = None):
        """Log successful completion of an operation"""
        self._complete_operation(operation_id, True, None, additional_metadata)
    
    def log_operation_error(self, operation_id: str, error_message: str, additional_metadata: Dict = None):
        """Log failed completion of an operation"""
        self._complete_operation(operation_id, False, error_message, additional_metadata)
    
    def _complete_operation(self, 
                          operation_id: str, 
                          success: bool, 
                          error_message: str = None,
                          additional_metadata: Dict = None):
        """Complete an operation and create audit entry"""
        with self._lock:
            if operation_id not in self._active_operations:
                logger.warning(f"Attempted to complete unknown operation: {operation_id}")
                return
            
            op_data = self._active_operations.pop(operation_id)
            end_time = time.time()
            duration_ms = (end_time - op_data['start_time']) * 1000
            
            # Update statistics
            self._operation_stats['total_operations'] += 1
            if success:
                self._operation_stats['successful_operations'] += 1
            else:
                self._operation_stats['failed_operations'] += 1
            
            op_type = op_data['operation_type']
            if op_type not in self._operation_stats['operations_by_type']:
                self._operation_stats['operations_by_type'][op_type] = {
                    'count': 0, 'success_count': 0, 'total_duration': 0.0
                }
            
            type_stats = self._operation_stats['operations_by_type'][op_type]
            type_stats['count'] += 1
            type_stats['total_duration'] += duration_ms
            if success:
                type_stats['success_count'] += 1
            
            # Update average duration
            total_ops = self._operation_stats['total_operations']
            current_avg = self._operation_stats['average_duration']
            self._operation_stats['average_duration'] = (
                (current_avg * (total_ops - 1) + duration_ms) / total_ops
            )
            
            # Create audit entry
            metadata = op_data['metadata'].copy()
            if additional_metadata:
                metadata.update(additional_metadata)
            
            entry = AuditEntry(
                timestamp=datetime.utcnow(),
                operation_id=operation_id,
                operation_type=op_data['operation_type'],
                user_uuid=op_data['user_uuid'] or 'unknown',
                company_uuid=op_data['company_uuid'] or 'unknown',
                requesting_user_uuid=op_data['requesting_user_uuid'],
                ip_address=op_data['ip_address'],
                user_agent=op_data['user_agent'],
                success=success,
                error_message=error_message,
                duration_ms=duration_ms,
                metadata=metadata
            )
            
            self._buffer.append(entry)
            
            # Flush if buffer is full
            if len(self._buffer) >= self._buffer_size:
                self._flush_buffer()
    
    def log_security_event(self, 
                         event_type: str,
                         user_uuid: str = None,
                         company_uuid: str = None,
                         severity: str = 'medium',
                         details: Dict = None):
        """Log security-related events"""
        operation_id = f"security_{int(time.time() * 1000)}"
        
        metadata = {
            'event_type': event_type,
            'severity': severity,
            'details': details or {}
        }
        
        self.log_operation_start(
            operation_id, 'security_event', user_uuid, company_uuid, 
            metadata=metadata
        )
        self.log_operation_success(operation_id)
    
    def get_audit_trail(self, 
                      company_uuid: str = None,
                      user_uuid: str = None,
                      start_date: str = None,
                      end_date: str = None,
                      operation_type: str = None,
                      limit: int = 1000) -> List[Dict]:
        """Get filtered audit trail"""
        try:
            entries = []
            
            # Parse date filters
            start_dt = None
            end_dt = None
            if start_date:
                start_dt = datetime.fromisoformat(start_date)
            if end_date:
                end_dt = datetime.fromisoformat(end_date)
            
            # Read from current buffer first
            with self._lock:
                for entry in reversed(self._buffer):
                    if self._matches_filters(entry, company_uuid, user_uuid, 
                                           start_dt, end_dt, operation_type):
                        entries.append(entry.to_dict())
                        if len(entries) >= limit:
                            return entries
            
            # Read from log files (most recent first)
            log_files = sorted(self.audit_dir.glob("audit_*.jsonl"), reverse=True)
            
            for log_file in log_files:
                if len(entries) >= limit:
                    break
                
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        
                    # Process in reverse order (most recent first)
                    for line in reversed(lines):
                        if len(entries) >= limit:
                            break
                        
                        try:
                            entry_data = json.loads(line.strip())
                            entry = AuditEntry.from_dict(entry_data)
                            
                            if self._matches_filters(entry, company_uuid, user_uuid,
                                                   start_dt, end_dt, operation_type):
                                entries.append(entry_data)
                        except (json.JSONDecodeError, KeyError, ValueError) as e:
                            logger.warning(f"Error parsing audit entry: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error reading audit log {log_file}: {e}")
                    continue
            
            return entries[:limit]
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
    
    def _matches_filters(self, 
                        entry: AuditEntry,
                        company_uuid: str = None,
                        user_uuid: str = None,
                        start_date: datetime = None,
                        end_date: datetime = None,
                        operation_type: str = None) -> bool:
        """Check if entry matches filter criteria"""
        if company_uuid and entry.company_uuid != company_uuid:
            return False
        
        if user_uuid and entry.user_uuid != user_uuid:
            return False
        
        if operation_type and entry.operation_type != operation_type:
            return False
        
        if start_date and entry.timestamp < start_date:
            return False
        
        if end_date and entry.timestamp > end_date:
            return False
        
        return True
    
    def get_operation_stats(self) -> Dict:
        """Get operation statistics"""
        with self._lock:
            stats = self._operation_stats.copy()
            
            # Calculate success rates for each operation type
            for op_type, type_stats in stats['operations_by_type'].items():
                count = type_stats['count']
                success_count = type_stats['success_count']
                total_duration = type_stats['total_duration']
                
                type_stats['success_rate'] = (success_count / count * 100) if count > 0 else 0
                type_stats['average_duration'] = total_duration / count if count > 0 else 0
            
            return stats
    
    def _flush_buffer(self):
        """Flush audit entries to disk"""
        if not self._buffer:
            return
        
        try:
            # Create log file with current date
            today = datetime.now().strftime("%Y%m%d")
            log_file = self.audit_dir / f"audit_{today}.jsonl"
            
            with open(log_file, 'a') as f:
                for entry in self._buffer:
                    f.write(json.dumps(entry.to_dict(), default=str) + '\n')
            
            logger.debug(f"Flushed {len(self._buffer)} audit entries to {log_file}")
            self._buffer.clear()
            self._last_flush = time.time()
            
        except Exception as e:
            logger.error(f"Error flushing audit buffer: {e}")
    
    def _flush_worker(self):
        """Background worker to periodically flush audit entries"""
        while True:
            try:
                time.sleep(self._flush_interval)
                
                with self._lock:
                    if (self._buffer and 
                        time.time() - self._last_flush > self._flush_interval):
                        self._flush_buffer()
                        
            except Exception as e:
                logger.error(f"Error in audit flush worker: {e}")
    
    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """Clean up old audit logs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            removed_count = 0
            
            for log_file in self.audit_dir.glob("audit_*.jsonl"):
                try:
                    # Extract date from filename
                    date_str = log_file.stem.split('_')[1]
                    file_date = datetime.strptime(date_str, "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        log_file.unlink()
                        removed_count += 1
                        logger.info(f"Removed old audit log: {log_file}")
                        
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse date from log file {log_file}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error removing log file {log_file}: {e}")
                    continue
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old audit logs: {e}")
            return 0
    
    def get_security_summary(self, 
                           company_uuid: str = None,
                           days: int = 30) -> Dict:
        """Get security event summary"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            security_events = self.get_audit_trail(
                company_uuid=company_uuid,
                start_date=start_date,
                operation_type='security_event'
            )
            
            summary = {
                'total_events': len(security_events),
                'events_by_severity': {},
                'events_by_type': {},
                'recent_events': security_events[:10]
            }
            
            for event in security_events:
                metadata = event.get('metadata', {})
                severity = metadata.get('severity', 'unknown')
                event_type = metadata.get('event_type', 'unknown')
                
                summary['events_by_severity'][severity] = (
                    summary['events_by_severity'].get(severity, 0) + 1
                )
                summary['events_by_type'][event_type] = (
                    summary['events_by_type'].get(event_type, 0) + 1
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting security summary: {e}")
            return {}
    
    def close(self):
        """Close audit service and flush remaining entries"""
        with self._lock:
            if self._buffer:
                self._flush_buffer()
        
        logger.info("Audit service closed")