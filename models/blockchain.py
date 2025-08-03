"""
Blockchain implementation for food supply chain
This handles the core blockchain functionality - blocks, chains, and mining
"""

import hashlib
import json
from datetime import datetime
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import pickle
import os
from models.database import db

class Block:
    """
    Individual block in the blockchain
    Each block contains transactions and is linked to the previous block
    """
    
    def __init__(self, index, transactions, previous_hash, nonce=0):
        """
        Initialize a new block
        
        Args:
            index: Position of block in chain (0, 1, 2, ...)
            transactions: List of transactions in this block
            previous_hash: Hash of the previous block
            nonce: Number used once (for proof of work)
        """
        self.index = index
        self.timestamp = datetime.utcnow().isoformat()
        self.transactions = transactions  # List of transaction data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """
        Calculate SHA-256 hash of the block
        This creates a unique fingerprint for the block
        """
        # Create string representation of block data
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.transactions, sort_keys=True)}{self.previous_hash}{self.nonce}"
        
        # Calculate SHA-256 hash
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        """
        Mine the block using Proof of Work
        Keep trying different nonce values until hash starts with required zeros
        
        Args:
            difficulty: Number of leading zeros required in hash
        """
        target = "0" * difficulty  # e.g., "00" for difficulty 2
        
        print(f"⛏️  Mining block {self.index}...")
        start_time = datetime.now()
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        end_time = datetime.now()
        time_taken = (end_time - start_time).total_seconds()
        
        print(f"✅ Block {self.index} mined! Hash: {self.hash}")
        print(f"⏱️  Time taken: {time_taken:.2f} seconds, Nonce: {self.nonce}")
    
    def to_dict(self):
        """
        Convert block to dictionary for JSON serialization
        """
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    def __repr__(self):
        return f"<Block {self.index}: {self.hash[:10]}...>"


class Transaction(db.Model):
    """
    Database model for transactions
    Also used to create transaction data for blockchain blocks
    """
    
    __tablename__ = 'transactions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Transaction identification
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    block_index = db.Column(db.Integer)  # Which block contains this transaction
    
    # Product and ownership
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(50), nullable=False)  # 'create', 'transfer', 'receive'
    quantity = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    
    # Location information
    location = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    
    # Environmental conditions at time of transaction
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    
    # Transport information
    vehicle_id = db.Column(db.String(50))
    transport_method = db.Column(db.String(50))  # 'truck', 'ship', 'plane', etc.
    expected_delivery = db.Column(db.DateTime)
    
    # Quality verification
    quality_check_passed = db.Column(db.Boolean, default=True)
    quality_notes = db.Column(db.Text)
    
    # Digital signature for verification
    signature = db.Column(db.Text)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, product_id, from_user_id, to_user_id, transaction_type, quantity, **kwargs):
        """
        Initialize new transaction
        """
        self.product_id = product_id
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.transaction_type = transaction_type
        self.quantity = quantity
        
        # Generate unique transaction ID
        self.transaction_id = self.generate_transaction_id()
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def generate_transaction_id(self):
        """
        Generate unique transaction ID
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_input = f"{self.product_id}{self.from_user_id}{self.to_user_id}{timestamp}"
        hash_result = hashlib.sha256(hash_input.encode()).hexdigest()[:10]
        return f"TX_{timestamp}_{hash_result}"
    
    def to_blockchain_dict(self):
        """
        Convert transaction to dictionary for blockchain storage
        """
        return {
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'vehicle_id': self.vehicle_id,
            'transport_method': self.transport_method,
            'quality_check_passed': self.quality_check_passed,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'signature': self.signature
        }
    
    def __repr__(self):
        return f"<Transaction {self.transaction_id}>"


class FoodChainBlockchain:
    """
    Main blockchain class for food supply chain
    Manages the chain of blocks and validates transactions
    """
    
    def __init__(self, difficulty=2):
        """
        Initialize blockchain
        
        Args:
            difficulty: Mining difficulty (number of leading zeros in hash)
        """
        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.mining_reward = 10  # Not used in supply chain, but good to have
        
        # Create genesis block (first block)
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """
        Create the first block in the chain (Genesis Block)
        """
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print("🎯 Genesis block created!")
    
    def get_latest_block(self):
        """
        Get the most recent block in the chain
        """
        return self.chain[-1]
    
    def add_transaction(self, transaction):
        """
        Add transaction to pending transactions
        
        Args:
            transaction: Transaction object or dictionary
        """
        if isinstance(transaction, Transaction):
            transaction_data = transaction.to_blockchain_dict()
        else:
            transaction_data = transaction
        
        self.pending_transactions.append(transaction_data)
        print(f"📝 Transaction added to pending: {transaction_data.get('transaction_id', 'Unknown')}")
    
    def mine_pending_transactions(self):
        """
        Mine all pending transactions into a new block
        """
        if not self.pending_transactions:
            print("❌ No pending transactions to mine!")
            return None
        
        # Create new block with pending transactions
        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash
        )
        
        # Mine the block
        block.mine_block(self.difficulty)
        
        # Add block to chain
        self.chain.append(block)
        
        # Update transaction records in database
        self.update_transaction_blocks(block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        print(f"✅ Block {block.index} added to blockchain!")
        return block
    
    def update_transaction_blocks(self, block):
        """
        Update database transactions with block information
        """
        for transaction_data in block.transactions:
            transaction_id = transaction_data.get('transaction_id')
            if transaction_id:
                transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
                if transaction:
                    transaction.block_index = block.index
                    db.session.commit()
    
    def validate_chain(self):
        """
        Validate the entire blockchain
        Check if all blocks are valid and properly linked
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Invalid hash at block {i}")
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Invalid previous hash at block {i}")
                return False
        
        print("✅ Blockchain is valid!")
        return True
    
    def get_balance(self, user_id):
        """
        Get transaction count for a user (not applicable for supply chain, but useful for analytics)
        """
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('from_user_id') == user_id:
                    balance -= 1
                if transaction.get('to_user_id') == user_id:
                    balance += 1
        return balance
    
    def get_product_history(self, product_id):
        """
        Get complete transaction history for a product
        """
        history = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('product_id') == product_id:
                    history.append({
                        'block_index': block.index,
                        'block_hash': block.hash,
                        'timestamp': block.timestamp,
                        'transaction': transaction
                    })
        return history
    
    def save_to_file(self, filename):
        """
        Save blockchain to file
        """
        try:
            blockchain_data = {
                'chain': [block.to_dict() for block in self.chain],
                'difficulty': self.difficulty,
                'pending_transactions': self.pending_transactions
            }
            
            filepath = os.path.join('data', filename)
            with open(filepath, 'w') as f:
                json.dump(blockchain_data, f, indent=2)
            
            print(f"💾 Blockchain saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving blockchain: {e}")
    
    def load_from_file(self, filename):
        """
        Load blockchain from file
        """
        try:
            filepath = os.path.join('data', filename)
            if not os.path.exists(filepath):
                print(f"📁 Blockchain file {filepath} not found. Creating new blockchain.")
                return
            
            with open(filepath, 'r') as f:
                blockchain_data = json.load(f)
            
            # Reconstruct chain
            self.chain = []
            for block_data in blockchain_data['chain']:
                block = Block(
                    index=block_data['index'],
                    transactions=block_data['transactions'],
                    previous_hash=block_data['previous_hash'],
                    nonce=block_data['nonce']
                )
                block.timestamp = block_data['timestamp']
                block.hash = block_data['hash']
                self.chain.append(block)
            
            self.difficulty = blockchain_data.get('difficulty', 2)
            self.pending_transactions = blockchain_data.get('pending_transactions', [])
            
            print(f"📂 Blockchain loaded from {filepath}")
            print(f"📊 Chain length: {len(self.chain)} blocks")
            
        except Exception as e:
            print(f"❌ Error loading blockchain: {e}")
            self.create_genesis_block()
    
    def get_chain_info(self):
        """
        Get blockchain statistics
        """
        total_transactions = sum(len(block.transactions) for block in self.chain)
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'pending_transactions': len(self.pending_transactions),
            'difficulty': self.difficulty,
            'latest_block_hash': self.get_latest_block().hash,
            'is_valid': self.validate_chain()
        }
    
    def __repr__(self):
        return f"<FoodChainBlockchain: {len(self.chain)} blocks>"


# Global blockchain instance
food_chain_blockchain = FoodChainBlockchain()

# Helper functions for easy use
def add_product_transaction(product_id, from_user_id, to_user_id, transaction_type, **kwargs):
    """
    Create and add a new product transaction to blockchain
    """
    # Create database transaction
    transaction = Transaction(
        product_id=product_id,
        from_user_id=from_user_id,
        to_user_id=to_user_id,
        transaction_type=transaction_type,
        quantity=kwargs.get('quantity', 1),
        **kwargs
    )
    
    # Save to database
    db.session.add(transaction)
    db.session.commit()
    
    # Add to blockchain
    food_chain_blockchain.add_transaction(transaction)
    
    return transaction

def mine_new_block():
    """
    Mine all pending transactions into a new block
    """
    return food_chain_blockchain.mine_pending_transactions()

def get_blockchain_info():
    """
    Get current blockchain information
    """
    return food_chain_blockchain.get_chain_info()

def save_blockchain():
    """
    Save blockchain to file
    """
    food_chain_blockchain.save_to_file('blockchain.json')

def load_blockchain():
    """
    Load blockchain from file
    """
    food_chain_blockchain.load_from_file('blockchain.json')