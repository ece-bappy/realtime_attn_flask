import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os

class DatabaseManager:
    """SQLite database manager for RFID logs"""
    
    def __init__(self, db_path: str = "rfid_logs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS card_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid TEXT NOT NULL,
                    user TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON card_logs(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user 
                ON card_logs(user)
            ''')
            
            conn.commit()
    
    def close(self):
        """Close database connection"""
        pass  # SQLite handles connections automatically

class CardLog:
    def __init__(self, uid: str, user: str, timestamp: Optional[datetime] = None, log_id: Optional[int] = None):
        self.id = log_id
        self.uid = uid
        self.user = user
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "time": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "uid": self.uid,
            "user": self.user
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CardLog':
        timestamp = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
        return cls(data["uid"], data["user"], timestamp, data.get("id"))

class LogManager:
    def __init__(self, db_path: str = "rfid_logs.db"):
        self.db_manager = DatabaseManager(db_path)
    
    def add_log(self, uid: str, user: str) -> CardLog:
        """Add a new log entry to database"""
        timestamp = datetime.now()
        
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO card_logs (uid, user, timestamp)
                VALUES (?, ?, ?)
            ''', (uid, user, timestamp))
            
            log_id = cursor.lastrowid
            conn.commit()
            
            return CardLog(uid, user, timestamp, log_id)
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent logs from database"""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, uid, user, timestamp
                FROM card_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            logs = []
            for row in cursor.fetchall():
                log = CardLog(row[1], row[2], datetime.fromisoformat(row[3]), row[0])
                logs.append(log.to_dict())
            
            return logs
    
    def get_stats(self) -> Dict:
        """Get statistics from database"""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Total scans
            cursor.execute('SELECT COUNT(*) FROM card_logs')
            total_scans = cursor.fetchone()[0]
            
            # Unique users
            cursor.execute('SELECT COUNT(DISTINCT user) FROM card_logs')
            unique_users = cursor.fetchone()[0]
            
            # Today's scans
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) FROM card_logs 
                WHERE DATE(timestamp) = DATE(?)
            ''', (today,))
            today_scans = cursor.fetchone()[0]
            
            return {
                "total_scans": total_scans,
                "unique_users": unique_users,
                "today_scans": today_scans
            }
    
    def search_logs(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Search logs by UID or user name"""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, uid, user, timestamp
                FROM card_logs
                WHERE uid LIKE ? OR user LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{search_term}%', f'%{search_term}%', limit))
            
            logs = []
            for row in cursor.fetchall():
                log = CardLog(row[1], row[2], datetime.fromisoformat(row[3]), row[0])
                logs.append(log.to_dict())
            
            return logs
    
    def get_logs_by_date(self, date: str, limit: int = 50) -> List[Dict]:
        """Get logs for a specific date (YYYY-MM-DD format)"""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, uid, user, timestamp
                FROM card_logs
                WHERE DATE(timestamp) = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (date, limit))
            
            logs = []
            for row in cursor.fetchall():
                log = CardLog(row[1], row[2], datetime.fromisoformat(row[3]), row[0])
                logs.append(log.to_dict())
            
            return logs
    
    def cleanup_old_logs(self, days_to_keep: int = 90):
        """Remove logs older than specified days"""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM card_logs
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count 