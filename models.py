"""
Database models for the cryptocurrency wallet application.
"""
from app import db
from datetime import datetime
from sqlalchemy import Index


class Wallet(db.Model):
    """
    Wallet model representing a cryptocurrency wallet.
    
    Attributes:
        id (int): Primary key
        address (str): Unique wallet address (public key)
        private_key (str): Encrypted private key
        balance (float): Current wallet balance
        created_at (datetime): Wallet creation timestamp
        is_multisig (bool): Whether this is a multi-signature wallet
        required_signatures (int): Number of signatures required for multisig
        two_factor_enabled (bool): Whether 2FA is enabled
        two_factor_secret (str): TOTP secret for 2FA
        backup_phrase (str): Encrypted backup phrase
        cryptocurrency_type (str): Type of cryptocurrency (BTC, ETH, etc.)
    """
    __tablename__ = 'wallets'
    
    id: int = db.Column(db.Integer, primary_key=True)
    address: str = db.Column(db.String(128), unique=True, nullable=False, index=True)
    private_key: str = db.Column(db.String(256), nullable=False)
    balance: float = db.Column(db.Float, default=0.0, nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Multi-signature support
    is_multisig: bool = db.Column(db.Boolean, default=False, nullable=False)
    required_signatures: int = db.Column(db.Integer, default=1, nullable=False)
    
    # Two-factor authentication
    two_factor_enabled: bool = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret: str = db.Column(db.String(32), nullable=True)
    
    # Backup and recovery
    backup_phrase: str = db.Column(db.String(512), nullable=True)
    
    # Multi-cryptocurrency support
    cryptocurrency_type: str = db.Column(db.String(10), default='COIN', nullable=False)
    
    # Relationships
    sent_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.sender_address',
        backref='sender',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    received_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.receiver_address',
        backref='receiver',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    # Multi-signature relationships
    multisig_owners = db.relationship(
        'MultisigOwner',
        backref='wallet',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of wallet."""
        return f'<Wallet {self.address[:10]}... Balance: {self.balance}>'
    
    def to_dict(self):
        """
        Convert wallet to dictionary.
        
        Returns:
            dict: Wallet data
        """
        return {
            'id': self.id,
            'address': self.address,
            'balance': round(self.balance, 8),
            'created_at': self.created_at.isoformat()
        }
    
    def update_balance(self, amount, operation='add'):
        """
        Update wallet balance.
        
        Args:
            amount (float): Amount to add or subtract
            operation (str): 'add' or 'subtract'
            
        Raises:
            ValueError: If operation is invalid or results in negative balance
        """
        if operation == 'add':
            self.balance += amount
        elif operation == 'subtract':
            if self.balance < amount:
                raise ValueError("Insufficient balance")
            self.balance -= amount
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        self.balance = round(self.balance, 8)


class Transaction(db.Model):
    """
    Transaction model representing a cryptocurrency transaction.
    
    Attributes:
        id (int): Primary key
        sender_address (str): Sender's wallet address
        receiver_address (str): Receiver's wallet address
        amount (float): Transaction amount
        timestamp (datetime): Transaction timestamp
        transaction_hash (str): Unique transaction hash
        status (str): Transaction status (pending, completed, failed)
    """
    __tablename__ = 'transactions'
    
    id: int = db.Column(db.Integer, primary_key=True)
    sender_address: str = db.Column(
        db.String(128), 
        db.ForeignKey('wallets.address', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    receiver_address: str = db.Column(
        db.String(128),
        db.ForeignKey('wallets.address', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    amount: float = db.Column(db.Float, nullable=False)
    timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    transaction_hash: str = db.Column(db.String(128), unique=True, nullable=False, index=True)
    status: str = db.Column(db.String(20), default='completed', nullable=False)
    
    # Create composite index for common queries
    __table_args__ = (
        Index('idx_sender_timestamp', 'sender_address', 'timestamp'),
        Index('idx_receiver_timestamp', 'receiver_address', 'timestamp'),
    )
    
    def __repr__(self):
        """String representation of transaction."""
        return f'<Transaction {self.transaction_hash[:10]}... {self.amount} coins>'
    
    def to_dict(self):
        """
        Convert transaction to dictionary.
        
        Returns:
            dict: Transaction data
        """
        return {
            'id': self.id,
            'sender_address': self.sender_address,
            'receiver_address': self.receiver_address,
            'amount': round(self.amount, 8),
            'timestamp': self.timestamp.isoformat(),
            'transaction_hash': self.transaction_hash,
            'status': self.status
        }
    
    @staticmethod
    def get_wallet_transactions(address, limit=None):
        """
        Get all transactions for a wallet address.
        
        Args:
            address (str): Wallet address
            limit (int, optional): Maximum number of transactions to return
            
        Returns:
            list: List of transactions
        """
        query = Transaction.query.filter(
            (Transaction.sender_address == address) |
            (Transaction.receiver_address == address)
        ).order_by(Transaction.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_balance(address):
        """
        Calculate balance from transactions.
        
        Args:
            address (str): Wallet address
            
        Returns:
            float: Calculated balance
        """
        received = db.session.query(
            db.func.sum(Transaction.amount)
        ).filter(
            Transaction.receiver_address == address,
            Transaction.status == 'completed'
        ).scalar() or 0.0
        
        sent = db.session.query(
            db.func.sum(Transaction.amount)
        ).filter(
            Transaction.sender_address == address,
            Transaction.status == 'completed'
        ).scalar() or 0.0
        
        return round(received - sent, 8)


class MultisigOwner(db.Model):
    """
    Multi-signature wallet owner model.
    
    Represents co-owners of a multi-signature wallet.
    """
    __tablename__ = 'multisig_owners'
    
    id: int = db.Column(db.Integer, primary_key=True)
    wallet_address: str = db.Column(
        db.String(128),
        db.ForeignKey('wallets.address', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    owner_address: str = db.Column(db.String(128), nullable=False)
    owner_name: str = db.Column(db.String(128), nullable=True)
    added_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'wallet_address': self.wallet_address,
            'owner_address': self.owner_address,
            'owner_name': self.owner_name,
            'added_at': self.added_at.isoformat()
        }


class TransactionSignature(db.Model):
    """
    Signature for multi-signature transactions.
    """
    __tablename__ = 'transaction_signatures'
    
    id: int = db.Column(db.Integer, primary_key=True)
    transaction_hash: str = db.Column(
        db.String(128),
        db.ForeignKey('transactions.transaction_hash', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    signer_address: str = db.Column(db.String(128), nullable=False)
    signature: str = db.Column(db.String(256), nullable=False)
    signed_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'signer_address': self.signer_address,
            'signed_at': self.signed_at.isoformat()
        }


class ExchangeRate(db.Model):
    """
    Exchange rate model for different cryptocurrencies.
    """
    __tablename__ = 'exchange_rates'
    
    id: int = db.Column(db.Integer, primary_key=True)
    from_currency: str = db.Column(db.String(10), nullable=False, index=True)
    to_currency: str = db.Column(db.String(10), nullable=False, index=True)
    rate: float = db.Column(db.Float, nullable=False)
    updated_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_currency_pair', 'from_currency', 'to_currency'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': self.rate,
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def get_rate(from_currency, to_currency):
        """Get exchange rate between two currencies."""
        rate = ExchangeRate.query.filter_by(
            from_currency=from_currency,
            to_currency=to_currency
        ).first()
        
        if rate:
            return rate.rate
        return 1.0  # Default to 1:1 if not found