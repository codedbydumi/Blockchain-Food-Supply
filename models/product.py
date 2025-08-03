"""
Product model for items in the supply chain
Tracks products from creation to final destination
"""

from models.database import db
from datetime import datetime, timedelta
import uuid

class Product(db.Model):
    """
    Product model representing items in the supply chain
    Each product has a unique batch ID and tracking information
    """
    
    __tablename__ = 'products'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Unique product identifier (like a serial number)
    batch_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Product information
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'vegetables', 'fruits', 'grains', etc.
    description = db.Column(db.Text)
    
    # Quantity and measurements
    quantity = db.Column(db.Float, nullable=False)  # Amount of product
    unit = db.Column(db.String(20), nullable=False)  # 'kg', 'tons', 'boxes', etc.
    
    # Quality information
    quality_grade = db.Column(db.String(10))  # 'A', 'B', 'C', or custom grading
    quality_score = db.Column(db.Integer)  # 0-100 quality score
    
    # Origin information
    origin_location = db.Column(db.String(200))  # Where product was produced
    harvest_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    
    # Current status
    current_location = db.Column(db.String(200))
    status = db.Column(db.String(50), default='created')  # 'created', 'in_transit', 'delivered', 'expired'
    
    # Environmental conditions (current)
    temperature = db.Column(db.Float)  # Celsius
    humidity = db.Column(db.Float)     # Percentage
    pressure = db.Column(db.Float)     # For certain products
    
    # Ownership
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    current_owner = db.relationship('User', foreign_keys=[current_owner_id], backref='owned_products')
    transactions = db.relationship('Transaction', backref='product', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, name, category, quantity, unit, created_by, **kwargs):
        """
        Initialize new product
        """
        self.name = name
        self.category = category
        self.quantity = quantity
        self.unit = unit
        self.created_by = created_by
        self.current_owner_id = created_by
        
        # Generate unique batch ID
        self.batch_id = self.generate_batch_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Set default expiry date if not provided
        if not self.expiry_date and self.harvest_date:
            # Default to 30 days after harvest
            self.expiry_date = self.harvest_date + timedelta(days=30)

    def generate_batch_id(self):
        """
        Generate unique batch ID for product
        Format: CATEGORY_TIMESTAMP_RANDOM
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        random_part = str(uuid.uuid4())[:8].upper()
        category_short = self.category[:3].upper()
        return f"{category_short}_{timestamp}_{random_part}"

    def is_expired(self):
        """
        Check if product has expired
        """
        if not self.expiry_date:
            return False
        return datetime.now().date() > self.expiry_date

    def days_until_expiry(self):
        """
        Calculate days until product expires
        Returns negative number if already expired
        """
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.now().date()
        return delta.days

    def is_fresh(self):
        """
        Check if product is still fresh (not expired and good quality)
        """
        return not self.is_expired() and self.quality_score and self.quality_score >= 70

    def update_environmental_conditions(self, temperature=None, humidity=None, pressure=None):
        """
        Update environmental conditions
        """
        if temperature is not None:
            self.temperature = temperature
        if humidity is not None:
            self.humidity = humidity
        if pressure is not None:
            self.pressure = pressure
        
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def transfer_ownership(self, new_owner_id):
        """
        Transfer product ownership to new user
        """
        old_owner_id = self.current_owner_id
        self.current_owner_id = new_owner_id
        self.updated_at = datetime.utcnow()
        
        # Update status
        if self.status == 'created':
            self.status = 'in_transit'
        
        db.session.commit()
        return old_owner_id

    def get_transaction_history(self):
        """
        Get all transactions for this product
        """
        return self.transactions.order_by('Transaction.timestamp.desc()').all()

    def get_current_location_info(self):
        """
        Get detailed current location information
        """
        latest_transaction = self.transactions.order_by('Transaction.timestamp.desc()').first()
        if latest_transaction:
            return {
                'location': latest_transaction.location,
                'coordinates': {
                    'latitude': latest_transaction.latitude,
                    'longitude': latest_transaction.longitude
                },
                'updated_at': latest_transaction.timestamp
            }
        return None

    def to_dict(self):
        """
        Convert product to dictionary
        """
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'quality_grade': self.quality_grade,
            'quality_score': self.quality_score,
            'origin_location': self.origin_location,
            'current_location': self.current_location,
            'status': self.status,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_expired': self.is_expired(),
            'days_until_expiry': self.days_until_expiry(),
            'is_fresh': self.is_fresh(),
            'created_by': self.created_by,
            'current_owner_id': self.current_owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        """
        String representation of product
        """
        return f'<Product {self.batch_id}: {self.name}>'

# Helper function to create sample products
def create_sample_products():
    """
    Create sample products for testing
    """
    from models.user import User
    
    # Get farmer user
    farmer = User.query.filter_by(role='farmer').first()
    if not farmer:
        print("❌ No farmer found. Create users first!")
        return
    
    sample_products = [
        {
            'name': 'Organic Tomatoes',
            'category': 'vegetables',
            'description': 'Fresh organic tomatoes from local farm',
            'quantity': 100.0,
            'unit': 'kg',
            'quality_grade': 'A',
            'quality_score': 95,
            'origin_location': 'Smith Organic Farm, California',
            'current_location': 'Farm Storage',
            'temperature': 18.5,
            'humidity': 65.0,
            'harvest_date': datetime.now().date(),
            'created_by': farmer.id
        },
        {
            'name': 'Fresh Apples',
            'category': 'fruits',
            'description': 'Crispy red apples',
            'quantity': 50.0,
            'unit': 'kg',
            'quality_grade': 'A',
            'quality_score': 90,
            'origin_location': 'Smith Organic Farm, California',
            'current_location': 'Farm Storage',
            'temperature': 15.0,
            'humidity': 70.0,
            'harvest_date': datetime.now().date(),
            'created_by': farmer.id
        }
    ]
    
    for product_data in sample_products:
        # Check if product already exists
        existing_product = Product.query.filter_by(name=product_data['name'], 
                                                 created_by=product_data['created_by']).first()
        if not existing_product:
            product = Product(**product_data)
            db.session.add(product)
    
    db.session.commit()
    print("✅ Sample products created!")