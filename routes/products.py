"""
Product management routes for supply chain operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
import json

from models.database import db
from models.user import User
from models.product import Product
from models.blockchain import Transaction, add_product_transaction, mine_new_block, food_chain_blockchain

# Create blueprint for product routes
products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required
def list_products():
    """
    List all products based on user role
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter products based on user role
    if current_user.role == 'farmer':
        # Farmers see products they created
        products = Product.query.filter_by(created_by=current_user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    elif current_user.role in ['distributor', 'retailer']:
        # Distributors and retailers see products they own
        products = Product.query.filter_by(current_owner_id=current_user.id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    else:
        # Inspectors see all products
        products = Product.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    return render_template('products/list.html', products=products)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """
    Add new product (farmers only)
    """
    if not current_user.can_create_products():
        flash('Only farmers can create products.', 'danger')
        return redirect(url_for('products.list_products'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        quantity = request.form.get('quantity', '0')
        unit = request.form.get('unit', '').strip()
        quality_grade = request.form.get('quality_grade', '').strip()
        quality_score = request.form.get('quality_score', '0')
        origin_location = request.form.get('origin_location', '').strip()
        current_location = request.form.get('current_location', '').strip()
        harvest_date = request.form.get('harvest_date', '')
        expiry_date = request.form.get('expiry_date', '')
        temperature = request.form.get('temperature', '0')
        humidity = request.form.get('humidity', '0')
        
        # Validate input
        errors = []
        if not name or len(name) < 2:
            errors.append('Product name must be at least 2 characters long.')
        if not category:
            errors.append('Please select a category.')
        
        try:
            quantity = float(quantity)
            if quantity <= 0:
                errors.append('Quantity must be greater than 0.')
        except ValueError:
            errors.append('Invalid quantity value.')
            quantity = 0
        
        if not unit:
            errors.append('Please specify the unit.')
        
        try:
            quality_score = int(quality_score)
            if quality_score < 0 or quality_score > 100:
                errors.append('Quality score must be between 0 and 100.')
        except ValueError:
            quality_score = 0
        
        try:
            temperature = float(temperature) if temperature else None
        except ValueError:
            temperature = None
        
        try:
            humidity = float(humidity) if humidity else None
        except ValueError:
            humidity = None
        
        # Parse dates
        harvest_date_obj = None
        expiry_date_obj = None
        
        if harvest_date:
            try:
                harvest_date_obj = datetime.strptime(harvest_date, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid harvest date format.')
        
        if expiry_date:
            try:
                expiry_date_obj = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid expiry date format.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('products/add.html')
        
        try:
            # Create product
            product = Product(
                name=name,
                category=category,
                description=description,
                quantity=quantity,
                unit=unit,
                quality_grade=quality_grade if quality_grade else None,
                quality_score=quality_score if quality_score > 0 else None,
                origin_location=origin_location if origin_location else None,
                current_location=current_location if current_location else None,
                harvest_date=harvest_date_obj,
                expiry_date=expiry_date_obj,
                temperature=temperature,
                humidity=humidity,
                created_by=current_user.id
            )
            
            db.session.add(product)
            db.session.flush()  # Get the product ID before committing
            
            # Create blockchain transaction for product creation
            transaction = add_product_transaction(
                product_id=product.id,
                from_user_id=current_user.id,
                to_user_id=current_user.id,  # Initially owned by creator
                transaction_type='create',
                quantity=quantity,
                location=current_location if current_location else None,
                temperature=temperature,
                humidity=humidity,
                notes=f'Product created: {name}'
            )
            
            # Commit all changes
            db.session.commit()
            
            # Mine new block
            mine_new_block()
            
            flash(f'Product "{name}" created successfully! Batch ID: {product.batch_id}', 'success')
            return redirect(url_for('products.view_product', id=product.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to create product: {str(e)}', 'danger')
            print(f"Product creation error: {e}")
            return render_template('products/add.html')
    
    # GET request - show the form
    return render_template('products/add.html')
@products_bp.route('/<int:id>')
@login_required
def view_product(id):
    """
    View detailed product information
    """
    product = Product.query.get_or_404(id)
    
    # Get transaction history from blockchain
    blockchain_history = food_chain_blockchain.get_product_history(product.id)
    
    # Get database transaction history
    db_transactions = product.get_transaction_history()
    
    # Check if user can transfer this product
    can_transfer = (
        current_user.id == product.current_owner_id and 
        current_user.can_transfer_products()
    )
    
    return render_template('products/view.html', 
                         product=product,
                         blockchain_history=blockchain_history,
                         db_transactions=db_transactions,
                         can_transfer=can_transfer)

@products_bp.route('/<int:id>/transfer', methods=['GET', 'POST'])
@login_required
def transfer_product(id):
    """
    Transfer product ownership
    """
    product = Product.query.get_or_404(id)
    
    # Check permissions
    if current_user.id != product.current_owner_id:
        flash('You can only transfer products you own.', 'danger')
        return redirect(url_for('products.view_product', id=id))
    
    if not current_user.can_transfer_products():
        flash('You do not have permission to transfer products.', 'danger')
        return redirect(url_for('products.view_product', id=id))
    
    if request.method == 'POST':
        # Get form data
        to_user_id = int(request.form.get('to_user_id'))
        quantity = float(product.quantity)  # Use full quantity for now
        location = request.form.get('location')
        
        # Safe conversions for optional fields
        try:
            latitude_str = request.form.get('latitude', '')
            latitude = float(latitude_str) if latitude_str.strip() else None
        except (ValueError, TypeError):
            latitude = None
            
        try:
            longitude_str = request.form.get('longitude', '')
            longitude = float(longitude_str) if longitude_str.strip() else None
        except (ValueError, TypeError):
            longitude = None
            
        try:
            temperature_str = request.form.get('temperature', '')
            temperature = float(temperature_str) if temperature_str.strip() else None
        except (ValueError, TypeError):
            temperature = None
            
        try:
            humidity_str = request.form.get('humidity', '')
            humidity = float(humidity_str) if humidity_str.strip() else None
        except (ValueError, TypeError):
            humidity = None
            
        vehicle_id = request.form.get('vehicle_id')
        transport_method = request.form.get('transport_method')
        notes = request.form.get('notes')
        
        # Validate
        to_user = User.query.get(to_user_id)
        if not to_user:
            flash('Invalid recipient selected.', 'danger')
            return render_template('products/transfer.html', product=product)
        
        if not to_user.can_receive_products():
            flash(f'{to_user.get_role_display()} cannot receive products.', 'danger')
            return render_template('products/transfer.html', product=product)
        
        try:
            # Transfer ownership
            old_owner_id = product.transfer_ownership(to_user_id)
            
            # Update product location and conditions
            if location:
                product.current_location = location
            if temperature is not None:
                product.temperature = temperature
            if humidity is not None:
                product.humidity = humidity
            
            db.session.commit()
            
            # Create blockchain transaction
            transaction = add_product_transaction(
                product_id=product.id,
                from_user_id=old_owner_id,
                to_user_id=to_user_id,
                transaction_type='transfer',
                quantity=quantity,
                location=location,
                latitude=latitude,
                longitude=longitude,
                temperature=temperature,
                humidity=humidity,
                vehicle_id=vehicle_id,
                transport_method=transport_method,
                notes=notes
            )
            
            # Mine new block
            mine_new_block()
            
            flash(f'Product transferred to {to_user.full_name} successfully!', 'success')
            return redirect(url_for('products.view_product', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash('Transfer failed. Please try again.', 'danger')
            print(f"Transfer error: {e}")
    
    # Get possible recipients based on current user role
    if current_user.role == 'farmer':
        recipients = User.query.filter_by(role='distributor').all()
    elif current_user.role == 'distributor':
        recipients = User.query.filter_by(role='retailer').all()
    else:
        recipients = []
    
    return render_template('products/transfer.html', product=product, recipients=recipients)

@products_bp.route('/<int:id>/history')
@login_required
def product_history(id):
    """
    View complete product history with blockchain verification
    """
    product = Product.query.get_or_404(id)
    
    # Get complete blockchain history
    blockchain_history = food_chain_blockchain.get_product_history(product.id)
    
    # Get database transactions for additional details
    db_transactions = {
        tx.transaction_id: tx for tx in product.get_transaction_history()
    }
    
    # Combine blockchain and database data
    complete_history = []
    for block_data in blockchain_history:
        transaction_data = block_data['transaction']
        tx_id = transaction_data.get('transaction_id')
        db_tx = db_transactions.get(tx_id)
        
        complete_history.append({
            'block_index': block_data['block_index'],
            'block_hash': block_data['block_hash'],
            'blockchain_data': transaction_data,
            'database_data': db_tx,
            'timestamp': block_data['timestamp']
        })
    
    return render_template('products/history.html', 
                         product=product, 
                         history=complete_history)

@products_bp.route('/search')
@login_required
def search_products():
    """
    Search products by various criteria
    """
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    
    # Build search query
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            (Product.name.contains(query)) | 
            (Product.batch_id.contains(query)) |
            (Product.description.contains(query))
        )
    
    if category:
        products_query = products_query.filter_by(category=category)
    
    if status:
        products_query = products_query.filter_by(status=status)
    
    # Apply role-based filtering
    if current_user.role == 'farmer':
        products_query = products_query.filter_by(created_by=current_user.id)
    elif current_user.role in ['distributor', 'retailer']:
        products_query = products_query.filter_by(current_owner_id=current_user.id)
    
    products = products_query.all()
    
    # Get available categories and statuses for filters
    categories = db.session.query(Product.category.distinct()).all()
    statuses = db.session.query(Product.status.distinct()).all()
    
    return render_template('products/search.html',
                         products=products,
                         categories=[c[0] for c in categories],
                         statuses=[s[0] for s in statuses],
                         current_query=query,
                         current_category=category,
                         current_status=status)

@products_bp.route('/api/batch/<batch_id>')
def api_product_by_batch(batch_id):
    """
    API endpoint to get product information by batch ID
    """
    product = Product.query.filter_by(batch_id=batch_id).first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    return jsonify(product.to_dict())

@products_bp.route('/api/<int:id>/track')
def api_track_product(id):
    """
    API endpoint for product tracking information
    """
    product = Product.query.get_or_404(id)
    
    # Get latest transaction for current location
    latest_transaction = product.transactions.order_by(Transaction.timestamp.desc()).first()
    
    tracking_info = {
        'product': product.to_dict(),
        'current_location': product.current_location,
        'current_owner': product.current_owner.full_name,
        'status': product.status,
        'last_update': latest_transaction.timestamp.isoformat() if latest_transaction else None,
        'environmental_conditions': {
            'temperature': product.temperature,
            'humidity': product.humidity,
            'pressure': product.pressure
        }
    }
    
    return jsonify(tracking_info)

@products_bp.route('/<int:id>/qr')
@login_required
def generate_qr_code(id):
    """
    Generate QR code for product tracking
    """
    product = Product.query.get_or_404(id)
    
    # QR code would contain URL to track the product
    tracking_url = url_for('products.api_track_product', id=product.id, _external=True)
    
    return render_template('products/qr_code.html', 
                         product=product, 
                         tracking_url=tracking_url)