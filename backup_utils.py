"""
Wallet backup and restore functionality.
"""
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import json
import logging

logger = logging.getLogger(__name__)


class BackupManager:
    """Manager for wallet backup and restore operations."""
    
    # Standard BIP39 word list (simplified - first 100 words for demo)
    WORD_LIST = [
        'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
        'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
        'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
        'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
        'advice', 'aerobic', 'affair', 'afford', 'afraid', 'again', 'age', 'agent',
        'agree', 'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album',
        'alcohol', 'alert', 'alien', 'all', 'alley', 'allow', 'almost', 'alone',
        'alpha', 'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among',
        'amount', 'amused', 'analyst', 'anchor', 'ancient', 'anger', 'angle', 'angry',
        'animal', 'ankle', 'announce', 'annual', 'another', 'answer', 'antenna', 'antique',
        'anxiety', 'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april',
        'arch', 'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor',
        'army', 'around', 'arrange', 'arrest', 'arrive', 'arrow'
    ]
    
    @staticmethod
    def generate_mnemonic(word_count=12):
        """
        Generate a mnemonic phrase for wallet backup.
        
        Args:
            word_count (int): Number of words (12, 15, 18, 21, or 24)
            
        Returns:
            str: Mnemonic phrase
        """
        if word_count not in [12, 15, 18, 21, 24]:
            word_count = 12
        
        # Generate random words
        words = []
        for _ in range(word_count):
            word = secrets.choice(BackupManager.WORD_LIST)
            words.append(word)
        
        return ' '.join(words)
    
    @staticmethod
    def encrypt_private_key(private_key, password):
        """
        Encrypt private key with password.
        
        Args:
            private_key (str): Private key to encrypt
            password (str): Password for encryption
            
        Returns:
            str: Encrypted private key
        """
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'crypto_wallet_salt',  # In production, use random salt
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Encrypt
            f = Fernet(key)
            encrypted = f.encrypt(private_key.encode())
            
            return encrypted.decode()
            
        except Exception as e:
            logger.error(f"Error encrypting private key: {e}")
            raise
    
    @staticmethod
    def decrypt_private_key(encrypted_key, password):
        """
        Decrypt private key with password.
        
        Args:
            encrypted_key (str): Encrypted private key
            password (str): Password for decryption
            
        Returns:
            str: Decrypted private key
        """
        try:
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'crypto_wallet_salt',
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_key.encode())
            
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting private key: {e}")
            raise
    
    @staticmethod
    def create_backup_data(wallet, password):
        """
        Create encrypted backup data for a wallet.
        
        Args:
            wallet: Wallet object
            password (str): Password for encryption
            
        Returns:
            dict: Backup data
        """
        try:
            # Generate mnemonic if not exists
            if not wallet.backup_phrase:
                mnemonic = BackupManager.generate_mnemonic()
            else:
                # Decrypt existing mnemonic
                mnemonic = BackupManager.decrypt_private_key(wallet.backup_phrase, password)
            
            backup_data = {
                'version': '1.0',
                'address': wallet.address,
                'mnemonic': mnemonic,
                'created_at': wallet.created_at.isoformat(),
                'cryptocurrency_type': wallet.cryptocurrency_type,
                'is_multisig': wallet.is_multisig,
            }
            
            # Encrypt backup data
            encrypted_backup = BackupManager.encrypt_private_key(
                json.dumps(backup_data),
                password
            )
            
            return {
                'encrypted_backup': encrypted_backup,
                'mnemonic': mnemonic  # Return for display (only once!)
            }
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    @staticmethod
    def restore_from_backup(encrypted_backup, password):
        """
        Restore wallet from encrypted backup.
        
        Args:
            encrypted_backup (str): Encrypted backup data
            password (str): Password for decryption
            
        Returns:
            dict: Wallet data
        """
        try:
            # Decrypt backup
            decrypted_json = BackupManager.decrypt_private_key(encrypted_backup, password)
            backup_data = json.loads(decrypted_json)
            
            return backup_data
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            raise
    
    @staticmethod
    def restore_from_mnemonic(mnemonic, password):
        """
        Restore wallet from mnemonic phrase.
        
        Args:
            mnemonic (str): Mnemonic phrase
            password (str): Password to encrypt the restored key
            
        Returns:
            dict: Wallet restoration data
        """
        try:
            words = mnemonic.strip().split()
            
            # Validate word count
            if len(words) not in [12, 15, 18, 21, 24]:
                raise ValueError("Invalid mnemonic phrase length")
            
            # Validate words are in word list
            for word in words:
                if word not in BackupManager.WORD_LIST:
                    # In production, validate against full BIP39 word list
                    logger.warning(f"Word '{word}' not in word list")
            
            # In production, derive private key from mnemonic using BIP39
            # For now, return validation success
            return {
                'valid': True,
                'mnemonic': mnemonic,
                'word_count': len(words)
            }
            
        except Exception as e:
            logger.error(f"Error restoring from mnemonic: {e}")
            raise
    
    @staticmethod
    def export_wallet_data(wallet):
        """
        Export wallet data (non-sensitive) for backup.
        
        Args:
            wallet: Wallet object
            
        Returns:
            dict: Exportable wallet data
        """
        return {
            'address': wallet.address,
            'balance': wallet.balance,
            'cryptocurrency_type': wallet.cryptocurrency_type,
            'created_at': wallet.created_at.isoformat(),
            'is_multisig': wallet.is_multisig,
            'two_factor_enabled': wallet.two_factor_enabled,
        }