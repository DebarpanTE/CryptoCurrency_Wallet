"""
Blockchain and transaction management module.
"""
import hashlib
import time
from datetime import datetime
from app import db
from app.models import Transaction, Wallet
from app.wallet import WalletManager, WalletError
import logging

logger = logging.getLogger(__name__)


class TransactionError(Exception):
    """Custom exception for transaction-related errors."""
    pass


class BlockchainManager:
    """Manager class for blockchain and transaction operations."""
    
    @staticmethod
    def calculate_hash(sender, receiver, amount, timestamp):
        """
        Calculate a unique hash for a transaction.
        
        Args:
            sender (str): Sender address
            receiver (str): Receiver address
            amount (float): Transaction amount
            timestamp (float): Unix timestamp
            
        Returns:
            str: Transaction hash
        """
        # Create a string with transaction data
        data = f"{sender}{receiver}{amount}{timestamp}"
        
        # Add some randomness to ensure uniqueness
        data += str(time.time())
        
        # Calculate SHA-256 hash
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def validate_transaction(sender_address, receiver_address, amount, private_key=None):
        """
        Validate a transaction before execution.
        
        Args:
            sender_address (str): Sender's wallet address
            receiver_address (str): Receiver's wallet address
            amount (float): Transaction amount
            private_key (str, optional): Sender's private key for verification
            
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        try:
            # Basic validation
            if not sender_address or not receiver_address:
                return False, "Sender and receiver addresses are required"
            
            if sender_address == receiver_address:
                return False, "Cannot send to yourself"
            
            if amount <= 0:
                return False, "Amount must be greater than zero"
            
            # Check if wallets exist
            sender_wallet = Wallet.query.filter_by(address=sender_address).first()
            receiver_wallet = Wallet.query.filter_by(address=receiver_address).first()
            
            if not sender_wallet:
                return False, f"Sender wallet not found: {sender_address}"
            
            if not receiver_wallet:
                return False, f"Receiver wallet not found: {receiver_address}"
            
            # Verify private key if provided
            if private_key:
                try:
                    if not WalletManager.verify_private_key(sender_address, private_key):
                        return False, "Invalid private key for sender wallet"
                except WalletError as e:
                    return False, str(e)
            
            # Check sufficient balance
            if sender_wallet.balance < amount:
                return False, f"Insufficient balance. Available: {sender_wallet.balance}, Required: {amount}"
            
            return True, "Transaction is valid"
            
        except Exception as e:
            logger.error(f"Error validating transaction: {e}")
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def create_transaction(sender_address, receiver_address, amount, private_key):
        """
        Create and execute a transaction.
        
        Args:
            sender_address (str): Sender's wallet address
            receiver_address (str): Receiver's wallet address
            amount (float): Transaction amount
            private_key (str): Sender's private key
            
        Returns:
            dict: Transaction details
            
        Raises:
            TransactionError: If transaction fails
        """
        try:
            # Validate transaction
            is_valid, error_message = BlockchainManager.validate_transaction(
                sender_address, receiver_address, amount, private_key
            )
            
            if not is_valid:
                raise TransactionError(error_message)
            
            # Get wallets
            sender_wallet = Wallet.query.filter_by(address=sender_address).first()
            receiver_wallet = Wallet.query.filter_by(address=receiver_address).first()
            
            # Round amount to 8 decimal places
            amount = round(amount, 8)
            
            # Calculate transaction hash
            timestamp = time.time()
            transaction_hash = BlockchainManager.calculate_hash(
                sender_address, receiver_address, amount, timestamp
            )
            
            # Create transaction record
            transaction = Transaction(
                sender_address=sender_address,
                receiver_address=receiver_address,
                amount=amount,
                transaction_hash=transaction_hash,
                status='completed'
            )
            
            # Update balances
            try:
                sender_wallet.update_balance(amount, 'subtract')
                receiver_wallet.update_balance(amount, 'add')
            except ValueError as e:
                raise TransactionError(str(e))
            
            # Commit to database
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Transaction completed: {transaction_hash}")
            
            # Emit real-time updates via WebSocket
            try:
                from app.websocket_events import emit_balance_update, emit_transaction_notification
                
                # Notify sender of balance update
                emit_balance_update(sender_address, sender_wallet.balance)
                
                # Notify receiver of balance update
                emit_balance_update(receiver_address, receiver_wallet.balance)
                
                # Notify both parties of the transaction
                tx_data = transaction.to_dict()
                emit_transaction_notification(sender_address, tx_data)
                emit_transaction_notification(receiver_address, tx_data)
            except Exception as ws_error:
                # Don't fail the transaction if WebSocket fails
                logger.warning(f"WebSocket notification failed: {ws_error}")
            
            return transaction.to_dict()
            
        except TransactionError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise TransactionError(f"Failed to create transaction: {str(e)}")
    
    @staticmethod
    def get_transaction(transaction_hash):
        """
        Retrieve a transaction by hash.
        
        Args:
            transaction_hash (str): Transaction hash
            
        Returns:
            Transaction: Transaction object
            
        Raises:
            TransactionError: If transaction not found
        """
        try:
            transaction = Transaction.query.filter_by(
                transaction_hash=transaction_hash
            ).first()
            
            if not transaction:
                raise TransactionError(f"Transaction not found: {transaction_hash}")
            
            return transaction
            
        except TransactionError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving transaction: {e}")
            raise TransactionError(f"Failed to retrieve transaction: {str(e)}")
    
    @staticmethod
    def get_wallet_transactions(address, limit=None):
        """
        Get all transactions for a wallet.
        
        Args:
            address (str): Wallet address
            limit (int, optional): Maximum number of transactions
            
        Returns:
            list: List of transaction dictionaries
            
        Raises:
            TransactionError: If retrieval fails
        """
        try:
            # Verify wallet exists
            if not WalletManager.wallet_exists(address):
                raise TransactionError(f"Wallet not found: {address}")
            
            transactions = Transaction.get_wallet_transactions(address, limit)
            
            return [t.to_dict() for t in transactions]
            
        except TransactionError:
            raise
        except Exception as e:
            logger.error(f"Error getting wallet transactions: {e}")
            raise TransactionError(f"Failed to get transactions: {str(e)}")
    
    @staticmethod
    def get_transaction_count(address):
        """
        Get the number of transactions for a wallet.
        
        Args:
            address (str): Wallet address
            
        Returns:
            dict: Transaction counts (sent, received, total)
        """
        try:
            sent_count = Transaction.query.filter_by(
                sender_address=address
            ).count()
            
            received_count = Transaction.query.filter_by(
                receiver_address=address
            ).count()
            
            return {
                'sent': sent_count,
                'received': received_count,
                'total': sent_count + received_count
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction count: {e}")
            return {'sent': 0, 'received': 0, 'total': 0}
    
    @staticmethod
    def get_recent_transactions(limit=10):
        """
        Get recent transactions across all wallets.
        
        Args:
            limit (int): Maximum number of transactions
            
        Returns:
            list: List of recent transactions
        """
        try:
            transactions = Transaction.query.order_by(
                Transaction.timestamp.desc()
            ).limit(limit).all()
            
            return [t.to_dict() for t in transactions]
            
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []