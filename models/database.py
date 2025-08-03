"""
Database setup and initialization
This file handles all database connections and table creation
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Create database instance
# This will be used throughout our application
db = SQLAlchemy()

def init_db(app):
    """
    Initialize database with Flask app
    This function connects our database to the Flask application
    """
    db.init_app(app)
    
    with app.app_context():
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Create all tables
        db.create_all()
        print("✅ Database initialized successfully!")

def reset_db(app):
    """
    Reset database (delete all data and recreate tables)
    Useful for development and testing
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("🔄 Database reset successfully!")