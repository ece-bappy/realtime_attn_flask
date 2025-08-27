import sqlite3
import shutil
import os
from datetime import datetime, timedelta
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseUtils:
    """Utility class for database maintenance and backup operations"""
    
    def __init__(self, db_path: str = "rfid_logs.db"):
        self.db_path = db_path
        self.backup_dir = "database_backups"
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the database"""
        try:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"rfid_logs_backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create backup
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            raise
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create a backup of current database before restore
            current_backup = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Database restored from backup: {backup_path}")
            logger.info(f"Previous state backed up to: {current_backup}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            raise
    
    def get_database_info(self) -> dict:
        """Get database information and statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get database size
                db_size = os.path.getsize(self.db_path)
                
                # Get row counts
                cursor.execute("SELECT COUNT(*) FROM card_logs")
                total_logs = cursor.fetchone()[0]
                
                # Get oldest and newest log dates
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM card_logs")
                date_range = cursor.fetchone()
                oldest_date = date_range[0] if date_range[0] else None
                newest_date = date_range[1] if date_range[1] else None
                
                # Get backup files info
                backup_files = []
                if os.path.exists(self.backup_dir):
                    for file in os.listdir(self.backup_dir):
                        if file.endswith('.db'):
                            file_path = os.path.join(self.backup_dir, file)
                            backup_files.append({
                                'name': file,
                                'size': os.path.getsize(file_path),
                                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                
                return {
                    'database_path': self.db_path,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'tables': tables,
                    'total_logs': total_logs,
                    'oldest_log': oldest_date,
                    'newest_log': newest_date,
                    'backup_count': len(backup_files),
                    'backup_files': backup_files,
                    'last_backup': max([b['modified'] for b in backup_files]) if backup_files else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get database info: {str(e)}")
            raise
    
    def optimize_database(self) -> dict:
        """Optimize database performance"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get initial size
                initial_size = os.path.getsize(self.db_path)
                
                # Analyze tables for better query planning
                cursor.execute("ANALYZE")
                
                # Vacuum database to reclaim space
                cursor.execute("VACUUM")
                
                # Reindex for better performance
                cursor.execute("REINDEX")
                
                # Get final size
                final_size = os.path.getsize(self.db_path)
                
                space_saved = initial_size - final_size
                
                logger.info(f"Database optimization completed. Space saved: {space_saved} bytes")
                
                return {
                    'initial_size_bytes': initial_size,
                    'final_size_bytes': final_size,
                    'space_saved_bytes': space_saved,
                    'space_saved_mb': round(space_saved / (1024 * 1024), 2),
                    'optimization_date': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to optimize database: {str(e)}")
            raise
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """Remove backup files older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            if os.path.exists(self.backup_dir):
                for file in os.listdir(self.backup_dir):
                    if file.endswith('.db'):
                        file_path = os.path.join(self.backup_dir, file)
                        file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_modified < cutoff_date:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.info(f"Deleted old backup: {file}")
            
            logger.info(f"Cleanup completed. Deleted {deleted_count} old backup files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            raise 