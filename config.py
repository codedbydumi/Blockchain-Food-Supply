import os
from datetime import timedelta

class Config:
    """
    Configuration class for our Flask application
    This stores all the settings we need
    """
    
    # Secret key for security (forms, sessions, etc.)
    # In real projects, this should be in environment variables
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    
    # Database configuration
    # We're using SQLite - a simple file-based database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'database.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    # How long users stay logged in
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Blockchain configuration
    BLOCKCHAIN_DIFFICULTY = 2  # How hard it is to mine a block (2 = easy for demo)
    BLOCKCHAIN_REWARD = 10     # Not used in our supply chain, but good to have
    
    # Application settings
    DEBUG = True               # Shows detailed errors (turn off in production)
    TESTING = False
    
    # File upload settings (if we add file uploads later)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Analytics settings
    ITEMS_PER_PAGE = 20        # How many items to show per page
    CHART_COLORS = [           # Colors for our charts
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
    ]


class DevelopmentConfig(Config):
    """
    Configuration for development (what we're using now)
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True     # Shows SQL queries in terminal (helpful for debugging)


class ProductionConfig(Config):
    """
    Configuration for production (when deployed to real server)
    """
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key'
    # In production, use environment variables for sensitive data


class TestingConfig(Config):
    """
    Configuration for testing
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use memory database for tests


# Dictionary to easily switch between configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}