"""
Dashboard routes for main application interface
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from models.database import db
from models.user import User
from models.product import Product
from models.blockchain import Transaction, get_blockchain_info

# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def main():
    """
    Main dashboard page
    Shows different content based on user role
    """
    # Get blockchain information
    blockchain_info = get_blockchain_info()
    
    # Get user statistics
    user_stats = get_user_statistics(current_user)
    
    # Get recent activities
    recent_activities = get_recent_activities(current_user)
    
    # Get system overview (for all users)
    system_overview = get_system_overview()
    
    return render_template('dashboard/main.html',
                         user=current_user,
                         blockchain_info=blockchain_info,
                         user_stats=user_stats,
                         recent_activities=recent_activities,
                         system_overview=system_overview)

@dashboard_bp.route('/overview')
@login_required
def overview():
    """
    System overview page with detailed statistics
    """
    # Get comprehensive system statistics
    stats = {
        'users': {
            'total': User.query.count(),
            'farmers': User.query.filter_by(role='farmer').count(),
            'distributors': User.query.filter_by(role='distributor').count(),
            'retailers': User.query.filter_by(role='retailer').count(),
            'inspectors': User.query.filter_by(role='inspector').count(),
        },
        'products': {
            'total': Product.query.count(),
            'active': Product.query.filter(Product.status != 'expired').count(),
            'expired': Product.query.filter(Product.status == 'expired').count(),
            'in_transit': Product.query.filter_by(status='in_transit').count(),
        },
        'transactions': {
            'total': Transaction.query.count(),
            'today': Transaction.query.filter(
                func.date(Transaction.timestamp) == datetime.now().date()
            ).count(),
            'this_week': Transaction.query.filter(
                Transaction.timestamp >= datetime.now() - timedelta(days=7)
            ).count(),
        }
    }
    
    # Get blockchain info
    blockchain_info = get_blockchain_info()
    
    # Get recent products
    recent_products = Product.query.order_by(desc(Product.created_at)).limit(10).all()
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(desc(Transaction.timestamp)).limit(10).all()
    
    return render_template('dashboard/overview.html',
                         stats=stats,
                         blockchain_info=blockchain_info,
                         recent_products=recent_products,
                         recent_transactions=recent_transactions)

def get_user_statistics(user):
    """
    Get statistics specific to the current user
    """
    from models.product import Product
    from models.blockchain import Transaction
    
    stats = {}
    
    if user.role == 'farmer':
        stats = {
            'products_created': Product.query.filter_by(created_by=user.id).count(),
            'active_products': Product.query.filter_by(created_by=user.id).filter(Product.status != 'expired').count(),
            'total_quantity': db.session.query(func.sum(Product.quantity)).filter_by(created_by=user.id).scalar() or 0,
            'transactions_sent': Transaction.query.filter_by(from_user_id=user.id).count(),
        }
    
    elif user.role in ['distributor', 'retailer']:
        stats = {
            'products_owned': Product.query.filter_by(current_owner_id=user.id).count(),
            'transactions_sent': Transaction.query.filter_by(from_user_id=user.id).count(),
            'transactions_received': Transaction.query.filter_by(to_user_id=user.id).count(),
            'products_in_transit': Product.query.filter_by(current_owner_id=user.id, status='in_transit').count(),
        }
    
    elif user.role == 'inspector':
        stats = {
            'total_products': Product.query.count(),
            'total_transactions': Transaction.query.count(),
            'products_inspected': 0,  # This could be enhanced with inspection records
            'quality_issues': Product.query.filter(Product.quality_score < 70).count(),
        }
    
    return stats

def get_recent_activities(user, limit=10):
    """
    Get recent activities for the current user
    """
    activities = []
    
    # Get recent transactions involving this user (avoid duplicates)
    recent_transactions = Transaction.query.filter(
        (Transaction.from_user_id == user.id) | (Transaction.to_user_id == user.id)
    ).order_by(desc(Transaction.timestamp)).limit(limit).all()
    
    for transaction in recent_transactions:
        # Determine activity type based on transaction type and user role
        if transaction.transaction_type == 'create':
            # Only show "Created" for product creation
            if transaction.from_user_id == user.id:
                activities.append({
                    'type': 'created',
                    'description': f"Created {transaction.product.name}",
                    'timestamp': transaction.timestamp,
                    'transaction': transaction
                })
        elif transaction.transaction_type == 'transfer':
            # Only show transfer activities for actual transfers
            if transaction.from_user_id == user.id and transaction.to_user_id != user.id:
                # User sent the product to someone else
                to_user = User.query.get(transaction.to_user_id)
                activities.append({
                    'type': 'sent',
                    'description': f"Sent {transaction.product.name} to {to_user.full_name if to_user else 'Unknown'}",
                    'timestamp': transaction.timestamp,
                    'transaction': transaction
                })
            elif transaction.to_user_id == user.id and transaction.from_user_id != user.id:
                # User received the product from someone else
                from_user = User.query.get(transaction.from_user_id)
                activities.append({
                    'type': 'received',
                    'description': f"Received {transaction.product.name} from {from_user.full_name if from_user else 'Unknown'}",
                    'timestamp': transaction.timestamp,
                    'transaction': transaction
                })
    
    # Get recently created products (for farmers) - but only if not already in transactions
    if user.role == 'farmer':
        recent_products = user.products_created.order_by(desc(Product.created_at)).limit(5).all()
        existing_product_ids = [activity['transaction'].product_id for activity in activities if 'transaction' in activity]
        
        for product in recent_products:
            if product.id not in existing_product_ids:
                activities.append({
                    'type': 'created',
                    'description': f"Created {product.name}",
                    'timestamp': product.created_at,
                    'product': product
                })
    
    # Sort activities by timestamp and remove duplicates
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Remove duplicate activities for the same product
    seen_activities = set()
    unique_activities = []
    
    for activity in activities:
        # Create a unique key for each activity
        if 'transaction' in activity:
            key = f"{activity['type']}_{activity['transaction'].product_id}_{activity['timestamp']}"
        else:
            key = f"{activity['type']}_{activity['product'].id}_{activity['timestamp']}"
        
        if key not in seen_activities:
            seen_activities.add(key)
            unique_activities.append(activity)
    
    return unique_activities[:limit]

def get_system_overview():
    """
    Get system-wide overview statistics
    """
    # Product categories distribution
    category_stats = db.session.query(
        Product.category, 
        func.count(Product.id).label('count')
    ).group_by(Product.category).all()
    
    # Quality distribution
    quality_stats = {
        'high_quality': Product.query.filter(Product.quality_score >= 80).count(),
        'medium_quality': Product.query.filter(
            (Product.quality_score >= 60) & (Product.quality_score < 80)
        ).count(),
        'low_quality': Product.query.filter(Product.quality_score < 60).count(),
    }
    
    # Temperature alerts (products outside safe range)
    temp_alerts = Product.query.filter(
        (Product.temperature < 0) | (Product.temperature > 25)
    ).count()
    
    return {
        'category_stats': dict(category_stats),
        'quality_stats': quality_stats,
        'temperature_alerts': temp_alerts,
        'blockchain_status': 'operational'  # This could be enhanced with actual checks
    }

@dashboard_bp.route('/api/quick_stats')
@login_required
def api_quick_stats():
    """
    API endpoint for quick statistics (for AJAX updates)
    """
    stats = get_user_statistics(current_user)
    return jsonify(stats)

@dashboard_bp.route('/api/recent_activities')
@login_required
def api_recent_activities():
    """
    API endpoint for recent activities (for AJAX updates)
    """
    activities = get_recent_activities(current_user, limit=5)
    
    # Convert to JSON-serializable format
    activities_json = []
    for activity in activities:
        activities_json.append({
            'type': activity['type'],
            'description': activity['description'],
            'timestamp': activity['timestamp'].isoformat(),
        })
    
    return jsonify(activities_json)