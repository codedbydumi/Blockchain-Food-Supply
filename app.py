"""
Main Flask application for Blockchain Food Supply Chain
This file initializes the app and connects all components
"""

from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
import os

# Import our models and configuration
from config import config
from models.database import db, init_db
from models.user import User, create_default_users
from models.product import Product, create_sample_products
from models.blockchain import load_blockchain, save_blockchain, get_blockchain_info

# Import route blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.products import products_bp
from routes.analytics import analytics_bp
from routes.blockchain import blockchain_bp  # NEW: Import blockchain routes


def create_app(config_name='development'):
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    init_db(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user for Flask-Login
        This function is called to reload the user object from the user ID stored in the session
        """
        return User.query.get(int(user_id))
    
    # Register blueprints (route groups)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(blockchain_bp, url_prefix='/blockchain')  # NEW: Register blockchain routes
    
    # Main routes
    @app.route('/')
    def index():
        """
        Home page - redirect based on user authentication
        """
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.main'))
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """
        About page explaining the blockchain food supply chain
        """
        blockchain_info = get_blockchain_info()
        return render_template('about.html', blockchain_info=blockchain_info)
    
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Handle 404 errors
        """
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 errors
        """
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Initialize data on first run
    with app.app_context():
        # Load blockchain from file
        load_blockchain()
        
        # Create default users and products if they don't exist
        if User.query.count() == 0:
            create_default_users()
            create_sample_products()
            print("🎯 Initial data created!")
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    """
    Run the application
    Only runs if this file is executed directly (not imported)
    """
    print("🚀 Starting Blockchain Food Supply Chain Application...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔗 Blockchain Explorer will be available at: http://localhost:5000/blockchain")  # NEW: Show blockchain URL
    print("👤 Default login credentials:")
    print("   Farmer: farmer_john / password123")
    print("   Distributor: distributor_abc / password123")
    print("   Retailer: retailer_fresh / password123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)