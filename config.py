import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # SocketIO settings
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Application settings
    MAX_LOGS_DISPLAY = 50
    TOAST_DURATION = 4000  # milliseconds
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'rfid_logs.db')
    DATABASE_BACKUP_ENABLED = os.environ.get('DATABASE_BACKUP_ENABLED', 'True').lower() == 'true'
    DATABASE_BACKUP_INTERVAL = int(os.environ.get('DATABASE_BACKUP_INTERVAL', 24))  # hours
    DATABASE_CLEANUP_DAYS = int(os.environ.get('DATABASE_CLEANUP_DAYS', 90))
    
    # Security settings
    MAX_LOG_LIMIT = 1000  # Maximum logs to return in single query
    RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'SECRET_KEY': cls.SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'HOST': cls.HOST,
            'PORT': cls.PORT,
            'SOCKETIO_ASYNC_MODE': cls.SOCKETIO_ASYNC_MODE,
            'SOCKETIO_CORS_ALLOWED_ORIGINS': cls.SOCKETIO_CORS_ALLOWED_ORIGINS,
            'MAX_LOGS_DISPLAY': cls.MAX_LOGS_DISPLAY,
            'TOAST_DURATION': cls.TOAST_DURATION,
            'DATABASE_PATH': cls.DATABASE_PATH,
            'DATABASE_BACKUP_ENABLED': cls.DATABASE_BACKUP_ENABLED,
            'DATABASE_BACKUP_INTERVAL': cls.DATABASE_BACKUP_INTERVAL,
            'DATABASE_CLEANUP_DAYS': cls.DATABASE_CLEANUP_DAYS,
            'MAX_LOG_LIMIT': cls.MAX_LOG_LIMIT,
            'RATE_LIMIT_ENABLED': cls.RATE_LIMIT_ENABLED
        } 