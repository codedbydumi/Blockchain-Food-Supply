# Add this to routes/blockchain.py (create new file)

"""
Blockchain explorer routes for viewing blockchain data
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.blockchain import food_chain_blockchain, get_blockchain_info
from models.product import Product
from models.user import User
import json

# Create blueprint for blockchain routes
blockchain_bp = Blueprint('blockchain', __name__)

@blockchain_bp.route('/')
@login_required
def explorer():
    """
    Main blockchain explorer page
    """
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get blockchain info
    blockchain_info = get_blockchain_info()
    
    # Get recent blocks (paginated)
    total_blocks = len(food_chain_blockchain.chain)
    start_index = max(0, total_blocks - (page * per_page))
    end_index = max(0, total_blocks - ((page - 1) * per_page))
    
    blocks = list(reversed(food_chain_blockchain.chain[start_index:end_index]))
    
    # Calculate pagination
    has_prev = page > 1
    has_next = start_index > 0
    
    return render_template('blockchain/explorer.html',
                         blocks=blocks,
                         blockchain_info=blockchain_info,
                         page=page,
                         per_page=per_page,
                         has_prev=has_prev,
                         has_next=has_next,
                         total_blocks=total_blocks)

@blockchain_bp.route('/block/<int:index>')
@login_required
def view_block(index):
    """
    View detailed information about a specific block
    """
    if index >= len(food_chain_blockchain.chain):
        flash('Block not found', 'danger')
        return redirect(url_for('blockchain.explorer'))
    
    block = food_chain_blockchain.chain[index]
    
    # Get transaction details with user and product info
    enhanced_transactions = []
    for tx in block.transactions:
        # Get related product and users
        product = Product.query.get(tx.product_id) if hasattr(tx, 'product_id') else None
        from_user = User.query.get(tx.from_user_id) if hasattr(tx, 'from_user_id') else None
        to_user = User.query.get(tx.to_user_id) if hasattr(tx, 'to_user_id') else None
        
        enhanced_transactions.append({
            'transaction': tx,
            'product': product,
            'from_user': from_user,
            'to_user': to_user
        })
    
    return render_template('blockchain/block_detail.html',
                         block=block,
                         enhanced_transactions=enhanced_transactions)

@blockchain_bp.route('/transaction/<transaction_id>')
@login_required
def view_transaction(transaction_id):
    """
    View detailed information about a specific transaction
    """
    # Find transaction in blockchain
    transaction_data = None
    block_index = None
    
    for i, block in enumerate(food_chain_blockchain.chain):
        for tx in block.transactions:
            if hasattr(tx, 'transaction_id') and str(tx.transaction_id) == str(transaction_id):
                transaction_data = {
                    'transaction': tx,
                    'block': block,
                    'block_index': i
                }
                break
        if transaction_data:
            break
    
    if not transaction_data:
        flash('Transaction not found', 'danger')
        return redirect(url_for('blockchain.explorer'))
    
    # Get related data
    product = Product.query.get(transaction_data['transaction'].product_id) if hasattr(transaction_data['transaction'], 'product_id') else None
    from_user = User.query.get(transaction_data['transaction'].from_user_id) if hasattr(transaction_data['transaction'], 'from_user_id') else None
    to_user = User.query.get(transaction_data['transaction'].to_user_id) if hasattr(transaction_data['transaction'], 'to_user_id') else None
    
    return render_template('blockchain/transaction_detail.html',
                         transaction_data=transaction_data,
                         product=product,
                         from_user=from_user,
                         to_user=to_user)

@blockchain_bp.route('/verify')
@login_required
def verify_blockchain():
    """
    Verify blockchain integrity
    """
    is_valid = food_chain_blockchain.is_chain_valid()
    
    # Get detailed verification results
    verification_results = []
    
    for i, block in enumerate(food_chain_blockchain.chain[1:], 1):  # Skip genesis block
        prev_block = food_chain_blockchain.chain[i - 1]
        
        # Check if block hash is valid
        block_valid = block.hash == block.calculate_hash()
        
        # Check if previous hash matches
        prev_hash_valid = block.previous_hash == prev_block.hash
        
        verification_results.append({
            'index': i,
            'block': block,
            'is_valid': block_valid and prev_hash_valid,
            'block_hash_valid': block_valid,
            'prev_hash_valid': prev_hash_valid
        })
    
    return render_template('blockchain/verification.html',
                         is_valid=is_valid,
                         verification_results=verification_results)

@blockchain_bp.route('/stats')
@login_required
def blockchain_stats():
    """
    Blockchain statistics and analytics
    """
    stats = {
        'total_blocks': len(food_chain_blockchain.chain),
        'total_transactions': sum(len(block.transactions) for block in food_chain_blockchain.chain),
        'chain_size': sum(len(str(block)) for block in food_chain_blockchain.chain),
        'average_block_size': 0,
        'mining_difficulty': food_chain_blockchain.difficulty if hasattr(food_chain_blockchain, 'difficulty') else 2,
    }
    
    if stats['total_blocks'] > 0:
        stats['average_block_size'] = stats['chain_size'] / stats['total_blocks']
    
    # Transaction types distribution
    tx_types = {}
    for block in food_chain_blockchain.chain:
        for tx in block.transactions:
            tx_type = getattr(tx, 'transaction_type', 'unknown')
            tx_types[tx_type] = tx_types.get(tx_type, 0) + 1
    
    # Daily transaction volume (last 30 days)
    from datetime import datetime, timedelta
    daily_volumes = {}
    
    for block in food_chain_blockchain.chain:
        block_date = datetime.fromisoformat(block.timestamp).date()
        daily_volumes[block_date] = daily_volumes.get(block_date, 0) + len(block.transactions)
    
    return render_template('blockchain/stats.html',
                         stats=stats,
                         tx_types=tx_types,
                         daily_volumes=daily_volumes)

@blockchain_bp.route('/api/search')
@login_required
def api_search():
    """
    Search blockchain by hash, transaction ID, or product batch ID
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    results = {
        'blocks': [],
        'transactions': [],
        'products': []
    }
    
    # Search blocks by hash
    for i, block in enumerate(food_chain_blockchain.chain):
        if query.lower() in block.hash.lower():
            results['blocks'].append({
                'index': i,
                'hash': block.hash,
                'timestamp': block.timestamp,
                'transaction_count': len(block.transactions)
            })
    
    # Search transactions
    for i, block in enumerate(food_chain_blockchain.chain):
        for tx in block.transactions:
            if (hasattr(tx, 'transaction_id') and query in str(tx.transaction_id)) or \
               (hasattr(tx, 'product_id') and query in str(tx.product_id)):
                results['transactions'].append({
                    'transaction_id': getattr(tx, 'transaction_id', 'N/A'),
                    'product_id': getattr(tx, 'product_id', 'N/A'),
                    'block_index': i,
                    'type': getattr(tx, 'transaction_type', 'unknown')
                })
    
    # Search products by batch ID
    products = Product.query.filter(Product.batch_id.contains(query)).all()
    for product in products:
        results['products'].append({
            'id': product.id,
            'name': product.name,
            'batch_id': product.batch_id,
            'category': product.category
        })
    
    return jsonify(results)