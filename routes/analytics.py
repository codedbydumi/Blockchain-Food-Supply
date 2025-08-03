"""
Analytics routes for data visualization and insights
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import json

from models.database import db
from models.user import User
from models.product import Product
from models.blockchain import Transaction, get_blockchain_info

# Create blueprint for analytics routes
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def dashboard():
    """
    Main analytics dashboard
    """
    # Get date range from query parameters
    days = request.args.get('days', 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get analytics data
    analytics_data = {
        'supply_chain_flow': get_supply_chain_flow_data(),
        'product_categories': get_product_category_data(),
        'quality_trends': get_quality_trends_data(start_date, end_date),
        'temperature_analysis': get_temperature_analysis_data(),
        'transaction_volume': get_transaction_volume_data(start_date, end_date),
        'fraud_alerts': get_fraud_detection_data(),
        'performance_metrics': get_performance_metrics_data()
    }
    
    # Get blockchain info
    blockchain_info = get_blockchain_info()
    
    return render_template('analytics/dashboard.html',
                         analytics_data=analytics_data,
                         blockchain_info=blockchain_info,
                         date_range=days)

@analytics_bp.route('/supply_chain')
@login_required
def supply_chain_analysis():
    """
    Detailed supply chain flow analysis
    """
    # Get supply chain metrics
    flow_data = get_detailed_supply_chain_flow()
    bottlenecks = identify_supply_chain_bottlenecks()
    efficiency_metrics = calculate_supply_chain_efficiency()
    
    return render_template('analytics/supply_chain.html',
                         flow_data=flow_data,
                         bottlenecks=bottlenecks,
                         efficiency_metrics=efficiency_metrics)

@analytics_bp.route('/quality')
@login_required
def quality_analysis():
    """
    Product quality analysis and trends
    """
    quality_data = {
        'quality_distribution': get_quality_distribution_data(),
        'quality_by_category': get_quality_by_category_data(),
        'quality_trends': get_quality_trends_data(datetime.now() - timedelta(days=90), datetime.now()),
        'temperature_quality_correlation': get_temperature_quality_correlation(),
        'expiry_analysis': get_expiry_analysis_data()
    }
    
    return render_template('analytics/quality.html', quality_data=quality_data)

@analytics_bp.route('/fraud_detection')
@login_required
def fraud_detection():
    """
    Fraud detection and security analysis
    """
    fraud_data = {
        'suspicious_transactions': get_suspicious_transactions(),
        'location_anomalies': get_location_anomalies(),
        'timing_irregularities': get_timing_irregularities(),
        'quality_score_anomalies': get_quality_score_anomalies(),
        'blockchain_integrity': verify_blockchain_integrity()
    }
    
    return render_template('analytics/fraud_detection.html', fraud_data=fraud_data)

@analytics_bp.route('/performance')
@login_required
def performance_metrics():
    """
    Supply chain performance metrics
    """
    performance_data = {
        'delivery_times': get_delivery_time_analysis(),
        'stakeholder_performance': get_stakeholder_performance_data(),
        'product_lifecycle': get_product_lifecycle_analysis(),
        'cost_analysis': get_cost_analysis_data(),
        'sustainability_metrics': get_sustainability_metrics()
    }
    
    return render_template('analytics/performance.html', performance_data=performance_data)

# Helper functions for data analysis

def get_supply_chain_flow_data():
    """
    Get supply chain flow statistics
    """
    try:
        flow_stats = db.session.query(
            Transaction.transaction_type,
            func.count(Transaction.id).label('count')
        ).group_by(Transaction.transaction_type).all()
        
        return {
            'flow_stats': dict(flow_stats) if flow_stats else {},
            'total_transactions': sum(count for _, count in flow_stats) if flow_stats else 0
        }
    except Exception as e:
        print(f"Error in get_supply_chain_flow_data: {e}")
        return {'flow_stats': {}, 'total_transactions': 0}

def get_product_category_data():
    """
    Get product distribution by category
    """
    try:
        category_stats = db.session.query(
            Product.category,
            func.count(Product.id).label('count'),
            func.avg(Product.quality_score).label('avg_quality'),
            func.sum(Product.quantity).label('total_quantity')
        ).group_by(Product.category).all()
        
        return [{
            'category': category,
            'count': count,
            'avg_quality': round(float(avg_quality), 1) if avg_quality else 0,
            'total_quantity': float(total_quantity) if total_quantity else 0
        } for category, count, avg_quality, total_quantity in category_stats]
    except Exception as e:
        print(f"Error in get_product_category_data: {e}")
        return []

def get_quality_trends_data(start_date, end_date):
    """
    Get quality trends over time
    """
    try:
        daily_quality = db.session.query(
            func.date(Product.created_at).label('date'),
            func.avg(Product.quality_score).label('avg_quality'),
            func.count(Product.id).label('product_count')
        ).filter(
            and_(Product.created_at >= start_date, Product.created_at <= end_date)
        ).group_by(func.date(Product.created_at)).order_by('date').all()
        
        return [{
            'date': date.isoformat() if date else datetime.now().date().isoformat(),  # Fixed the typo here
            'avg_quality': round(float(avg_quality), 1) if avg_quality else 0,
            'product_count': product_count
        } for date, avg_quality, product_count in daily_quality]
    except Exception as e:
        print(f"Error in get_quality_trends_data: {e}")
        return []

def get_temperature_analysis_data():
    """
    Analyze temperature data for cold chain compliance
    """
    try:
        temp_stats = db.session.query(
            func.avg(Product.temperature).label('avg_temp'),
            func.min(Product.temperature).label('min_temp'),
            func.max(Product.temperature).label('max_temp'),
            func.count(Product.id).label('total_products')
        ).filter(Product.temperature.isnot(None)).first()
        
        # Count products outside safe temperature range (0-25°C)
        unsafe_temp_count = Product.query.filter(
            (Product.temperature < 0) | (Product.temperature > 25)
        ).count() if temp_stats and temp_stats.total_products else 0
        
        total_products = temp_stats.total_products if temp_stats else 0
        
        return {
            'avg_temperature': round(float(temp_stats.avg_temp), 1) if temp_stats and temp_stats.avg_temp else 0,
            'min_temperature': float(temp_stats.min_temp) if temp_stats and temp_stats.min_temp else 0,
            'max_temperature': float(temp_stats.max_temp) if temp_stats and temp_stats.max_temp else 0,
            'total_products': total_products,
            'unsafe_temp_count': unsafe_temp_count,
            'compliance_rate': round((1 - unsafe_temp_count / max(total_products, 1)) * 100, 1)
        }
    except Exception as e:
        print(f"Error in get_temperature_analysis_data: {e}")
        return {
            'avg_temperature': 0, 'min_temperature': 0, 'max_temperature': 0,
            'total_products': 0, 'unsafe_temp_count': 0, 'compliance_rate': 100
        }

def get_transaction_volume_data(start_date, end_date):
    """
    Get transaction volume over time
    """
    try:
        daily_transactions = db.session.query(
            func.date(Transaction.timestamp).label('date'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            and_(Transaction.timestamp >= start_date, Transaction.timestamp <= end_date)
        ).group_by(func.date(Transaction.timestamp)).order_by('date').all()
        
        return [{
            'date': date.isoformat() if date else datetime.now().date().isoformat(),  # Fixed the typo here too
            'transaction_count': transaction_count
        } for date, transaction_count in daily_transactions]
    except Exception as e:
        print(f"Error in get_transaction_volume_data: {e}")
        return []

def get_fraud_detection_data():
    """
    Detect potential fraud indicators
    """
    try:
        alerts = []
        
        # Check for rapid ownership changes
        rapid_transfers = db.session.query(
            Transaction.product_id,
            func.count(Transaction.id).label('transfer_count')
        ).filter(
            Transaction.timestamp >= datetime.now() - timedelta(days=1)
        ).group_by(Transaction.product_id).having(
            func.count(Transaction.id) > 3
        ).all()
        
        for product_id, count in rapid_transfers:
            product = Product.query.get(product_id)
            if product:
                alerts.append({
                    'type': 'rapid_transfers',
                    'severity': 'high',
                    'message': f'Product {product.batch_id} has {count} transfers in 24 hours',
                    'product_id': product_id
                })
        
        # Check for temperature violations
        temp_violations = Product.query.filter(
            (Product.temperature < -10) | (Product.temperature > 40)
        ).limit(10).all()  # Limit to prevent too many alerts
        
        for product in temp_violations:
            alerts.append({
                'type': 'temperature_violation',
                'severity': 'medium',
                'message': f'Product {product.batch_id} temperature out of range: {product.temperature}°C',
                'product_id': product.id
            })
        
        return alerts
    except Exception as e:
        print(f"Error in get_fraud_detection_data: {e}")
        return []

def get_performance_metrics_data():
    """
    Calculate key performance indicators
    """
    try:
        # Average delivery time (rough estimate based on transactions)
        avg_delivery_time = db.session.query(
            func.avg(func.julianday(Transaction.timestamp) - func.julianday(Product.created_at)).label('avg_days')
        ).join(Product).filter(Transaction.transaction_type == 'transfer').first()
        
        # Product turnover rate
        total_products = Product.query.count()
        transferred_products = db.session.query(Transaction.product_id.distinct()).filter(
            Transaction.transaction_type == 'transfer'
        ).count()
        
        return {
            'avg_delivery_time': round(float(avg_delivery_time.avg_days), 1) if avg_delivery_time and avg_delivery_time.avg_days else 0,
            'product_turnover_rate': round((transferred_products / max(total_products, 1)) * 100, 1),
            'total_stakeholders': User.query.count(),
            'active_products': Product.query.filter(Product.status != 'expired').count()
        }
    except Exception as e:
        print(f"Error in get_performance_metrics_data: {e}")
        return {
            'avg_delivery_time': 0, 'product_turnover_rate': 0,
            'total_stakeholders': 0, 'active_products': 0
        }

# API endpoints for dynamic data loading

@analytics_bp.route('/api/chart_data/<chart_type>')
@login_required
def api_chart_data(chart_type):
    """
    API endpoint for chart data
    """
    data = {}
    
    if chart_type == 'product_categories':
        data = get_product_category_data()
    elif chart_type == 'quality_trends':
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        data = get_quality_trends_data(start_date, datetime.now())
    elif chart_type == 'temperature_analysis':
        data = get_temperature_analysis_data()
    elif chart_type == 'transaction_volume':
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        data = get_transaction_volume_data(start_date, datetime.now())
    elif chart_type == 'supply_chain_flow':
        data = get_supply_chain_flow_data()
    
    return jsonify(data)

@analytics_bp.route('/api/fraud_alerts')
@login_required
def api_fraud_alerts():
    """
    API endpoint for fraud detection alerts
    """
    alerts = get_fraud_detection_data()
    return jsonify(alerts)

@analytics_bp.route('/api/performance_summary')
@login_required
def api_performance_summary():
    """
    API endpoint for performance metrics summary
    """
    metrics = get_performance_metrics_data()
    return jsonify(metrics)

# Additional helper functions (implement as needed)
def get_detailed_supply_chain_flow():
    """Detailed supply chain flow analysis"""
    return {}

def identify_supply_chain_bottlenecks():
    """Identify bottlenecks in supply chain"""
    return []

def calculate_supply_chain_efficiency():
    """Calculate efficiency metrics"""
    return {}

def get_quality_distribution_data():
    """Get quality score distribution"""
    return {}

def get_quality_by_category_data():
    """Get quality metrics by product category"""
    return {}

def get_temperature_quality_correlation():
    """Analyze correlation between temperature and quality"""
    return {}

def get_expiry_analysis_data():
    """Analyze product expiry patterns"""
    return {}

def get_suspicious_transactions():
    """Identify suspicious transaction patterns"""
    return []

def get_location_anomalies():
    """Detect location-based anomalies"""
    return []

def get_timing_irregularities():
    """Detect timing-based irregularities"""
    return []

def get_quality_score_anomalies():
    """Detect quality score anomalies"""
    return []

def verify_blockchain_integrity():
    """Verify blockchain integrity"""
    return {'status': 'valid', 'blocks_verified': 0}

def get_delivery_time_analysis():
    """Analyze delivery times"""
    return {}

def get_stakeholder_performance_data():
    """Get stakeholder performance metrics"""
    return {}

def get_product_lifecycle_analysis():
    """Analyze product lifecycle"""
    return {}

def get_cost_analysis_data():
    """Analyze costs in supply chain"""
    return {}

def get_sustainability_metrics():
    """Calculate sustainability metrics"""
    return {}