"""
User model for stakeholders in the supply chain
Handles farmers, distributors, retailers, and inspectors
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models.database import db

class User(UserMixin, db.Model):
    """
    User model for all stakeholders in the supply chain
    
    UserMixin provides Flask-Login functionality:
    - is_authenticated, is_active, is_anonymous, get_id()
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic user information
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # User profile
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # User role in supply chain
    role = db.Column(db.String(20), nullable=False)  # 'farmer', 'distributor', 'retailer', 'inspector'
    
    # Business information
    company_name = db.Column(db.String(100))
    license_number = db.Column(db.String(50))  # Business license or certification
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)  # For business verification
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    # Products created by this user (if farmer)
    products_created = db.relationship('Product', foreign_keys='Product.created_by', 
                                     backref='creator', lazy='dynamic')
    
    # Transactions where this user is sender
    sent_transactions = db.relationship('Transaction', foreign_keys='Transaction.from_user_id', 
                                      backref='sender', lazy='dynamic')
    
    # Transactions where this user is receiver
    received_transactions = db.relationship('Transaction', foreign_keys='Transaction.to_user_id', 
                                          backref='receiver', lazy='dynamic')

    def __init__(self, username, email, password, full_name, role, **kwargs):
        """
        Initialize new user
        **kwargs allows additional parameters like company_name, phone, etc.
        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.full_name = full_name
        self.role = role
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_password(self, password):
        """
        Hash and store password securely
        We never store plain text passwords!
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if provided password matches stored hash
        Returns True if password is correct
        """
        return check_password_hash(self.password_hash, password)

    def get_role_display(self):
        """
        Get user-friendly role name
        """
        role_names = {
            'farmer': 'Farmer/Producer',
            'distributor': 'Distributor',
            'retailer': 'Retailer',
            'inspector': 'Inspector'
        }
        return role_names.get(self.role, self.role.title())

    def can_create_products(self):
        """
        Check if user can create new products
        Only farmers can create products
        """
        return self.role == 'farmer'

    def can_transfer_products(self):
        """
        Check if user can transfer products
        Farmers and distributors can transfer
        """
        return self.role in ['farmer', 'distributor']

    def can_receive_products(self):
        """
        Check if user can receive products
        Distributors and retailers can receive
        """
        return self.role in ['distributor', 'retailer']

    def update_last_login(self):
        """
        Update last login timestamp
        """
        self.last_login = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """
        Convert user to dictionary (useful for API responses)
        Excludes sensitive information like password_hash
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'role_display': self.get_role_display(),
            'company_name': self.company_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        """
        String representation of user (for debugging)
        """
        return f'<User {self.username} ({self.role})>'

# Helper function to create default users
def create_default_users():
    """
    Create some default users for testing
    """
    default_users = [
        {
            'username': 'farmer_john',
            'email': 'john@farm.com',
            'password': 'password123',
            'full_name': 'John Smith',
            'role': 'farmer',
            'company_name': 'Smith Organic Farm',
            'license_number': 'FARM001'
        },
        {
            'username': 'distributor_abc',
            'email': 'contact@abcdist.com',
            'password': 'password123',
            'full_name': 'ABC Distribution',
            'role': 'distributor',
            'company_name': 'ABC Distribution Ltd',
            'license_number': 'DIST001'
        },
        {
            'username': 'retailer_fresh',
            'email': 'manager@freshmart.com',
            'password': 'password123',
            'full_name': 'Fresh Mart',
            'role': 'retailer',
            'company_name': 'Fresh Mart Supermarket',
            'license_number': 'RET001'
        }
    ]
    
    for user_data in default_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(**user_data)
            user.is_verified = True  # Auto-verify default users
            db.session.add(user)
    
    db.session.commit()
    print("✅ Default users created!")