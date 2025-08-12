"""
Blockchain explorer routes for viewing blockchain data
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.blockchain import food_chain_blockchain, get_blockchain_info
from models.product import Product
from models.user import User
from models.blockchain import Transaction
from models.database import db
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
    
    # Get total blocks
    total_blocks = len(food_chain_blockchain.chain)
    
    if total_blocks == 0:
        return render_template('blockchain/explorer.html',
                             blocks=[],
                             blockchain_info=blockchain_info,
                             page=page,
                             per_page=per_page,
                             has_prev=False,
                             has_next=False,
                             total_blocks=0)
    
    # Calculate pagination indices (reverse order - newest first)
    start_index = max(0, total_blocks - (page * per_page))
    end_index = min(total_blocks, total_blocks - ((page - 1) * per_page))
    
    # Get blocks in reverse order (newest first)
    blocks = []
    for i in range(end_index - 1, start_index - 1, -1):
        if i >= 0 and i < len(food_chain_blockchain.chain):
            blocks.append(food_chain_blockchain.chain[i])
    
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
    if index >= len(food_chain_blockchain.chain) or index < 0:
        flash('Block not found', 'danger')
        return redirect(url_for('blockchain.explorer'))
    
    block = food_chain_blockchain.chain[index]
    
    # Get transaction details with user and product info
    enhanced_transactions = []
    for tx in block.transactions:
        # Get related product and users
        product = None
        from_user = None
        to_user = None
        
        if hasattr(tx, 'product_id') and tx.product_id:
            product = Product.query.get(tx.product_id)
        
        if hasattr(tx, 'from_user_id') and tx.from_user_id:
            from_user = User.query.get(tx.from_user_id)
            
        if hasattr(tx, 'to_user_id') and tx.to_user_id:
            to_user = User.query.get(tx.to_user_id)
        
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
    product = None
    from_user = None
    to_user = None
    
    if hasattr(transaction_data['transaction'], 'product_id') and transaction_data['transaction'].product_id:
        product = Product.query.get(transaction_data['transaction'].product_id)
    
    if hasattr(transaction_data['transaction'], 'from_user_id') and transaction_data['transaction'].from_user_id:
        from_user = User.query.get(transaction_data['transaction'].from_user_id)
        
    if hasattr(transaction_data['transaction'], 'to_user_id') and transaction_data['transaction'].to_user_id:
        to_user = User.query.get(transaction_data['transaction'].to_user_id)
    
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
    # Simple verification - check if chain exists and has blocks
    is_valid = len(food_chain_blockchain.chain) > 0
    
    # Get detailed verification results
    verification_results = []
    
    if len(food_chain_blockchain.chain) > 1:
        for i, block in enumerate(food_chain_blockchain.chain[1:], 1):  # Skip genesis block
            prev_block = food_chain_blockchain.chain[i - 1] if i > 0 else None
            
            # Basic checks
            block_valid = True
            prev_hash_valid = True
            
            try:
                # Check if block hash exists
                block_valid = hasattr(block, 'hash') and block.hash and len(block.hash) > 0
                
                # Check if previous hash matches (if we have a previous block)
                if prev_block:
                    prev_hash_valid = (hasattr(block, 'previous_hash') and 
                                     hasattr(prev_block, 'hash') and
                                     block.previous_hash == prev_block.hash)
            except Exception as e:
                print(f"Verification error for block {i}: {e}")
                block_valid = False
                prev_hash_valid = False
            
            verification_results.append({
                'index': i,
                'block': block,
                'is_valid': block_valid and prev_hash_valid,
                'block_hash_valid': block_valid,
                'prev_hash_valid': prev_hash_valid
            })
    
    # Overall validation
    is_valid = all(result['is_valid'] for result in verification_results) if verification_results else True
    
    return render_template('blockchain/verification.html',
                         is_valid=is_valid,
                         verification_results=verification_results)

@blockchain_bp.route('/stats')
@login_required
def blockchain_stats():
    """
    Blockchain statistics and analytics
    """
    chain = food_chain_blockchain.chain
    
    stats = {
        'total_blocks': len(chain),
        'total_transactions': sum(len(block.transactions) for block in chain),
        'chain_size_bytes': sum(len(str(block)) for block in chain),
        'average_block_size': 0,
        'mining_difficulty': getattr(food_chain_blockchain, 'difficulty', 2),
        'genesis_timestamp': chain[0].timestamp if chain else None,
        'latest_timestamp': chain[-1].timestamp if chain else None
    }
    
    if stats['total_blocks'] > 0:
        stats['average_block_size'] = stats['chain_size_bytes'] / stats['total_blocks']
    
    # Transaction types distribution
    tx_types = {}
    for block in chain:
        for tx in block.transactions:
            tx_type = getattr(tx, 'transaction_type', 'unknown')
            tx_types[tx_type] = tx_types.get(tx_type, 0) + 1
    
    # Daily transaction volume (last 30 days)
    from datetime import datetime, timedelta
    daily_volumes = {}
    
    for block in chain:
        try:
            if hasattr(block, 'timestamp') and block.timestamp:
                # Handle different timestamp formats
                if isinstance(block.timestamp, str):
                    # Try parsing ISO format
                    try:
                        block_date = datetime.fromisoformat(block.timestamp.replace('Z', '+00:00')).date()
                    except ValueError:
                        # Try other common formats
                        try:
                            block_date = datetime.strptime(block.timestamp[:19], '%Y-%m-%d %H:%M:%S').date()
                        except ValueError:
                            continue
                else:
                    block_date = block.timestamp.date()
                    
                daily_volumes[block_date.isoformat()] = daily_volumes.get(block_date.isoformat(), 0) + len(block.transactions)
        except Exception as e:
            print(f"Error processing block timestamp: {e}")
            continue
    
    # Block size distribution
    block_sizes = []
    for block in chain:
        try:
            block_sizes.append(len(str(block)))
        except:
            block_sizes.append(0)
    
    return render_template('blockchain/stats.html',
                         stats=stats,
                         tx_types=tx_types,
                         daily_volumes=daily_volumes,
                         block_sizes=block_sizes)

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
    
    try:
        # Search blocks by hash or index
        for i, block in enumerate(food_chain_blockchain.chain):
            try:
                block_hash = getattr(block, 'hash', '')
                if (query.lower() in block_hash.lower()) or (str(i) == query):
                    results['blocks'].append({
                        'index': i,
                        'hash': block_hash,
                        'timestamp': getattr(block, 'timestamp', ''),
                        'transaction_count': len(getattr(block, 'transactions', []))
                    })
            except Exception as e:
                print(f"Error searching block {i}: {e}")
                continue
        
        # Search transactions
        for i, block in enumerate(food_chain_blockchain.chain):
            try:
                for tx in getattr(block, 'transactions', []):
                    tx_id = getattr(tx, 'transaction_id', None)
                    product_id = getattr(tx, 'product_id', None)
                    
                    if (tx_id and query in str(tx_id)) or (product_id and query in str(product_id)):
                        results['transactions'].append({
                            'transaction_id': tx_id or 'N/A',
                            'product_id': product_id or 'N/A',
                            'block_index': i,
                            'type': getattr(tx, 'transaction_type', 'unknown')
                        })
            except Exception as e:
                print(f"Error searching transactions in block {i}: {e}")
                continue
        
        # Search products by batch ID or name
        try:
            products = Product.query.filter(
                (Product.batch_id.contains(query)) | 
                (Product.name.contains(query))
            ).limit(10).all()
            
            for product in products:
                results['products'].append({
                    'id': product.id,
                    'name': product.name,
                    'batch_id': product.batch_id,
                    'category': product.category
                })
        except Exception as e:
            print(f"Error searching products: {e}")
    
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
    
    return jsonify(results)

@blockchain_bp.route('/api/block/<int:index>')
@login_required
def api_block_detail(index):
    """
    API endpoint for block details
    """
    if index >= len(food_chain_blockchain.chain) or index < 0:
        return jsonify({'error': 'Block not found'}), 404
    
    try:
        block = food_chain_blockchain.chain[index]
        
        # Convert block to dictionary
        block_data = {
            'index': getattr(block, 'index', index),
            'hash': getattr(block, 'hash', ''),
            'previous_hash': getattr(block, 'previous_hash', ''),
            'timestamp': getattr(block, 'timestamp', ''),
            'nonce': getattr(block, 'nonce', 0),
            'transactions': []
        }
        
        # Add transaction data
        for tx in getattr(block, 'transactions', []):
            try:
                tx_data = {
                    'transaction_id': getattr(tx, 'transaction_id', None),
                    'transaction_type': getattr(tx, 'transaction_type', 'unknown'),
                    'product_id': getattr(tx, 'product_id', None),
                    'from_user_id': getattr(tx, 'from_user_id', None),
                    'to_user_id': getattr(tx, 'to_user_id', None),
                    'quantity': getattr(tx, 'quantity', None),
                    'location': getattr(tx, 'location', None),
                    'temperature': getattr(tx, 'temperature', None),
                    'humidity': getattr(tx, 'humidity', None)
                }
                block_data['transactions'].append(tx_data)
            except Exception as e:
                print(f"Error processing transaction: {e}")
                continue
        
        return jsonify(block_data)
    
    except Exception as e:
        print(f"Error getting block details: {e}")
        return jsonify({'error': f'Failed to get block details: {str(e)}'}), 500

@blockchain_bp.route('/network')
@login_required
def network_status():
    """
    Show blockchain network status and peers (for future multi-node support)
    """
    try:
        network_info = {
            'node_id': 'local-node-001',  # This would be dynamic in a real network
            'network_status': 'operational',
            'connected_peers': 0,  # No peers in local setup
            'sync_status': 'synchronized',
            'last_block_time': food_chain_blockchain.chain[-1].timestamp if food_chain_blockchain.chain else None,
            'blockchain_height': len(food_chain_blockchain.chain)
        }
    except Exception as e:
        print(f"Error getting network status: {e}")
        network_info = {
            'node_id': 'local-node-001',
            'network_status': 'error',
            'connected_peers': 0,
            'sync_status': 'unknown',
            'last_block_time': None,
            'blockchain_height': 0
        }
    
    return render_template('blockchain/network.html', network_info=network_info)