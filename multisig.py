"""
Multi-signature wallet management.
"""
from app import db
from app.models import Wallet, MultisigOwner, Transaction, TransactionSignature
from app.wallet import WalletManager, WalletError
import logging

logger = logging.getLogger(__name__)


class MultisigError(Exception):
    """Custom exception for multi-signature wallet errors."""
    pass


class MultisigManager:
    """Manager for multi-signature wallet operations."""
    
    @staticmethod
    def create_multisig_wallet(owner_addresses, required_signatures, initial_balance=0.0):
        """
        Create a multi-signature wallet.
        
        Args:
            owner_addresses (list): List of owner wallet addresses
            required_signatures (int): Number of signatures required
            initial_balance (float): Initial balance
            
        Returns:
            dict: Multi-signature wallet data
            
        Raises:
            MultisigError: If creation fails
        """
        try:
            # Validate inputs
            if not owner_addresses or len(owner_addresses) < 2:
                raise MultisigError("Multi-sig wallet requires at least 2 owners")
            
            if required_signatures < 1 or required_signatures > len(owner_addresses):
                raise MultisigError(
                    f"Required signatures must be between 1 and {len(owner_addresses)}"
                )
            
            # Verify all owner addresses exist
            for address in owner_addresses:
                if not WalletManager.wallet_exists(address):
                    raise MultisigError(f"Owner wallet not found: {address}")
            
            # Create the multisig wallet
            wallet_data = WalletManager.create_wallet(initial_balance)
            
            # Update wallet to be multisig
            wallet = Wallet.query.filter_by(address=wallet_data['address']).first()
            wallet.is_multisig = True
            wallet.required_signatures = required_signatures
            
            # Add owners
            for owner_address in owner_addresses:
                owner = MultisigOwner(
                    wallet_address=wallet.address,
                    owner_address=owner_address
                )
                db.session.add(owner)
            
            db.session.commit()
            
            logger.info(f"Created multisig wallet: {wallet.address}")
            
            return {
                'address': wallet.address,
                'private_key': wallet_data['private_key'],
                'balance': wallet.balance,
                'is_multisig': True,
                'required_signatures': required_signatures,
                'owners': owner_addresses,
                'created_at': wallet.created_at.isoformat()
            }
            
        except MultisigError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating multisig wallet: {e}")
            raise MultisigError(f"Failed to create multisig wallet: {str(e)}")
    
    @staticmethod
    def get_multisig_owners(wallet_address):
        """
        Get all owners of a multi-signature wallet.
        
        Args:
            wallet_address (str): Multi-sig wallet address
            
        Returns:
            list: List of owner dictionaries
        """
        try:
            owners = MultisigOwner.query.filter_by(
                wallet_address=wallet_address
            ).all()
            
            return [owner.to_dict() for owner in owners]
            
        except Exception as e:
            logger.error(f"Error getting multisig owners: {e}")
            return []
    
    @staticmethod
    def add_signature(transaction_hash, signer_address, signature):
        """
        Add a signature to a pending multisig transaction.
        
        Args:
            transaction_hash (str): Transaction hash
            signer_address (str): Signer's wallet address
            signature (str): Signature
            
        Returns:
            bool: True if signature added successfully
        """
        try:
            # Check if already signed
            existing = TransactionSignature.query.filter_by(
                transaction_hash=transaction_hash,
                signer_address=signer_address
            ).first()
            
            if existing:
                raise MultisigError("Already signed by this address")
            
            # Add signature
            sig = TransactionSignature(
                transaction_hash=transaction_hash,
                signer_address=signer_address,
                signature=signature
            )
            
            db.session.add(sig)
            db.session.commit()
            
            logger.info(f"Signature added by {signer_address} for {transaction_hash}")
            return True
            
        except MultisigError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding signature: {e}")
            return False
    
    @staticmethod
    def get_signature_count(transaction_hash):
        """
        Get number of signatures for a transaction.
        
        Args:
            transaction_hash (str): Transaction hash
            
        Returns:
            int: Number of signatures
        """
        try:
            count = TransactionSignature.query.filter_by(
                transaction_hash=transaction_hash
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting signature count: {e}")
            return 0
    
    @staticmethod
    def is_transaction_approved(transaction_hash):
        """
        Check if a multisig transaction has enough signatures.
        
        Args:
            transaction_hash (str): Transaction hash
            
        Returns:
            bool: True if transaction has enough signatures
        """
        try:
            # Get transaction
            transaction = Transaction.query.filter_by(
                transaction_hash=transaction_hash
            ).first()
            
            if not transaction:
                return False
            
            # Get sender wallet
            wallet = Wallet.query.filter_by(
                address=transaction.sender_address
            ).first()
            
            if not wallet or not wallet.is_multisig:
                return True  # Non-multisig transactions are auto-approved
            
            # Check signature count
            sig_count = MultisigManager.get_signature_count(transaction_hash)
            
            return sig_count >= wallet.required_signatures
            
        except Exception as e:
            logger.error(f"Error checking transaction approval: {e}")
            return False
    
    @staticmethod
    def get_pending_transactions(wallet_address):
        """
        Get pending multisig transactions for a wallet.
        
        Args:
            wallet_address (str): Wallet address
            
        Returns:
            list: List of pending transactions
        """
        try:
            # Get all pending transactions where this wallet is sender
            pending = Transaction.query.filter_by(
                sender_address=wallet_address,
                status='pending'
            ).all()
            
            results = []
            for tx in pending:
                sig_count = MultisigManager.get_signature_count(tx.transaction_hash)
                wallet = Wallet.query.filter_by(address=wallet_address).first()
                
                results.append({
                    **tx.to_dict(),
                    'signatures_count': sig_count,
                    'required_signatures': wallet.required_signatures if wallet else 1,
                    'is_approved': sig_count >= (wallet.required_signatures if wallet else 1)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending transactions: {e}")
            return []
    
    @staticmethod
    def is_owner(wallet_address, user_address):
        """
        Check if a user is an owner of a multisig wallet.
        
        Args:
            wallet_address (str): Multi-sig wallet address
            user_address (str): User's wallet address
            
        Returns:
            bool: True if user is an owner
        """
        try:
            owner = MultisigOwner.query.filter_by(
                wallet_address=wallet_address,
                owner_address=user_address
            ).first()
            
            return owner is not None
            
        except Exception as e:
            logger.error(f"Error checking ownership: {e}")
            return False