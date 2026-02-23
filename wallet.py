"""
Wallet management module for creating and managing cryptocurrency wallets.
"""
import hashlib
import secrets
from ecdsa import SigningKey, SECP256k1
from app import db
from app.models import Wallet
import logging

logger = logging.getLogger(__name__)


class WalletError(Exception):
    """Custom exception for wallet-related errors."""
    pass


class WalletManager:
    """Manager class for wallet operations."""
    
    @staticmethod
    def generate_keys():
        """
        Generate a new private/public key pair.
        
        Returns:
            tuple: (private_key, public_key) as hex strings
            
        Raises:
            WalletError: If key generation fails
        """
        try:
            # Generate private key using SECP256k1 elliptic curve
            private_key = SigningKey.generate(curve=SECP256k1)
            public_key = private_key.get_verifying_key()
            
            # Convert to hex strings
            private_key_hex = private_key.to_string().hex()
            public_key_hex = public_key.to_string().hex()
            
            return private_key_hex, public_key_hex
        except Exception as e:
            logger.error(f"Error generating keys: {e}")
            raise WalletError(f"Failed to generate keys: {str(e)}")
    
    @staticmethod
    def create_address(public_key):
        """
        Create a wallet address from a public key.
        
        Args:
            public_key (str): Public key in hex format
            
        Returns:
            str: Wallet address
            
        Raises:
            WalletError: If address creation fails
        """
        try:
            # Hash the public key using SHA-256
            sha256_hash = hashlib.sha256(public_key.encode()).hexdigest()
            
            # Take first 40 characters and add prefix
            address = '0x' + sha256_hash[:40]
            
            return address
        except Exception as e:
            logger.error(f"Error creating address: {e}")
            raise WalletError(f"Failed to create address: {str(e)}")
    
    @staticmethod
    def hash_private_key(private_key):
        """
        Hash a private key for storage.
        
        Args:
            private_key (str): Private key in hex format
            
        Returns:
            str: Hashed private key
        """
        return hashlib.sha256(private_key.encode()).hexdigest()
    
    @staticmethod
    def create_wallet(initial_balance=0.0):
        """
        Create a new wallet with generated keys.
        
        Args:
            initial_balance (float): Initial balance for the wallet
            
        Returns:
            dict: Wallet information including private key (only shown once)
            
        Raises:
            WalletError: If wallet creation fails
        """
        try:
            # Generate keys
            private_key, public_key = WalletManager.generate_keys()
            
            # Create address
            address = WalletManager.create_address(public_key)
            
            # Check if wallet already exists
            existing_wallet = Wallet.query.filter_by(address=address).first()
            if existing_wallet:
                raise WalletError("Wallet with this address already exists")
            
            # Hash private key for storage
            hashed_private_key = WalletManager.hash_private_key(private_key)
            
            # Create wallet in database
            wallet = Wallet(
                address=address,
                private_key=hashed_private_key,
                balance=initial_balance
            )
            
            db.session.add(wallet)
            db.session.commit()
            
            logger.info(f"Created new wallet: {address}")
            
            # Return wallet info (private key only shown here)
            return {
                'address': address,
                'private_key': private_key,  # WARNING: Only shown once!
                'balance': initial_balance,
                'created_at': wallet.created_at.isoformat()
            }
            
        except WalletError:
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating wallet: {e}")
            raise WalletError(f"Failed to create wallet: {str(e)}")
    
    @staticmethod
    def verify_private_key(address, private_key):
        """
        Verify that a private key belongs to a wallet address.
        
        Args:
            address (str): Wallet address
            private_key (str): Private key to verify
            
        Returns:
            bool: True if private key is valid
            
        Raises:
            WalletError: If verification fails or wallet not found
        """
        try:
            wallet = Wallet.query.filter_by(address=address).first()
            
            if not wallet:
                raise WalletError("Wallet not found")
            
            # Hash provided private key and compare
            hashed_key = WalletManager.hash_private_key(private_key)
            
            return hashed_key == wallet.private_key
            
        except WalletError:
            raise
        except Exception as e:
            logger.error(f"Error verifying private key: {e}")
            raise WalletError(f"Failed to verify private key: {str(e)}")
    
    @staticmethod
    def get_wallet(address):
        """
        Retrieve a wallet by address.
        
        Args:
            address (str): Wallet address
            
        Returns:
            Wallet: Wallet object
            
        Raises:
            WalletError: If wallet not found
        """
        try:
            wallet = Wallet.query.filter_by(address=address).first()
            
            if not wallet:
                raise WalletError(f"Wallet not found: {address}")
            
            return wallet
            
        except WalletError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving wallet: {e}")
            raise WalletError(f"Failed to retrieve wallet: {str(e)}")
    
    @staticmethod
    def get_balance(address):
        """
        Get the balance of a wallet.
        
        Args:
            address (str): Wallet address
            
        Returns:
            float: Wallet balance
            
        Raises:
            WalletError: If wallet not found
        """
        try:
            wallet = WalletManager.get_wallet(address)
            return round(wallet.balance, 8)
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise WalletError(f"Failed to get balance: {str(e)}")
    
    @staticmethod
    def wallet_exists(address):
        """
        Check if a wallet exists.
        
        Args:
            address (str): Wallet address
            
        Returns:
            bool: True if wallet exists
        """
        try:
            wallet = Wallet.query.filter_by(address=address).first()
            return wallet is not None
        except Exception as e:
            logger.error(f"Error checking wallet existence: {e}")
            return False
    
    @staticmethod
    def verify_wallet(address, private_key):
        """
        Verify wallet credentials by checking if the private key matches the address.
        
        Args:
            address (str): Wallet address
            private_key (str): Private key to verify
            
        Returns:
            bool: True if credentials are valid
            
        Raises:
            WalletError: If wallet not found
        """
        try:
            # Check if wallet exists
            wallet = Wallet.query.filter_by(address=address).first()
            
            if not wallet:
                raise WalletError("Wallet not found")
            
            # Regenerate address from private key to verify
            try:
                # Import SigningKey and SECP256k1
                from ecdsa import SigningKey, SECP256k1
                
                # Convert hex private key to bytes
                private_key_bytes = bytes.fromhex(private_key)
                
                # Create signing key from private key
                signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
                
                # Get public key
                public_key = signing_key.get_verifying_key()
                public_key_hex = public_key.to_string().hex()
                
                # Generate address from public key
                generated_address = WalletManager.create_address(public_key_hex)
                
                # Compare addresses
                if generated_address == address:
                    logger.info(f"Wallet credentials verified for: {address}")
                    return True
                else:
                    logger.warning(f"Private key does not match wallet address: {address}")
                    return False
                    
            except Exception as key_error:
                logger.error(f"Error verifying private key: {key_error}")
                return False
                
        except WalletError:
            raise
        except Exception as e:
            logger.error(f"Error verifying wallet: {e}")
            raise WalletError(f"Failed to verify wallet: {str(e)}")