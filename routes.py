"""
Flask routes for the cryptocurrency wallet application.
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, Response
from app.wallet import WalletManager, WalletError
from app.blockchain import BlockchainManager, TransactionError
from app.models import Wallet
from app import db
from config import Config
import logging

# Import new utilities
from app.qr_utils import QRCodeGenerator
from app.export_utils import ExportManager
from app.two_factor import TwoFactorAuth
from app.exchange_rates import ExchangeRateManager
from app.backup_utils import BackupManager

logger = logging.getLogger(__name__)

# Create Blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@main_bp.route('/create_wallet', methods=['POST'])
def create_wallet():
    """
    Create a new cryptocurrency wallet.
    
    Returns:
        JSON response with wallet details or error
    """
    try:
        # Get initial balance from config
        initial_balance = Config.INITIAL_BALANCE
        
        # Create wallet
        wallet_data = WalletManager.create_wallet(initial_balance)
        
        logger.info(f"Wallet created successfully: {wallet_data['address']}")
        
        return jsonify({
            'success': True,
            'message': 'Wallet created successfully',
            'data': wallet_data
        }), 201
        
    except WalletError as e:
        logger.error(f"Wallet creation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error in wallet creation: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/access_wallet', methods=['POST'])
def access_wallet():
    """
    Verify wallet credentials and grant access.
    
    Returns:
        JSON response indicating success or failure
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        address = data.get('address', '').strip()
        private_key = data.get('private_key', '').strip()
        
        if not address or not private_key:
            return jsonify({
                'success': False,
                'error': 'Address and private key are required'
            }), 400
        
        # Verify credentials
        if WalletManager.verify_wallet(address, private_key):
            # Store in session
            session['wallet_address'] = address
            session['authenticated'] = True
            
            logger.info(f"Wallet accessed: {address}")
            
            return jsonify({
                'success': True,
                'message': 'Access granted',
                'address': address
            }), 200
        else:
            logger.warning(f"Failed access attempt for wallet: {address}")
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
            
    except WalletError as e:
        logger.error(f"Wallet access failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Unexpected error in wallet access: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/wallet/<address>')
def wallet_page(address):
    """
    Display wallet dashboard page.
    
    Args:
        address (str): Wallet address
        
    Returns:
        Rendered template or redirect
    """
    try:
        # Get wallet
        wallet = WalletManager.get_wallet(address)
        
        # Render wallet page
        return render_template(
            'wallet.html',
            address=wallet.address,
            balance=wallet.balance
        )
        
    except WalletError as e:
        flash(f'Wallet not found: {str(e)}', 'error')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Error loading wallet page: {e}")
        flash('An error occurred loading the wallet', 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/get_balance/<address>', methods=['GET'])
def get_balance(address):
    """
    Get wallet balance.
    
    Args:
        address (str): Wallet address
        
    Returns:
        JSON response with balance
    """
    try:
        balance = WalletManager.get_balance(address)
        
        return jsonify({
            'success': True,
            'data': {
                'address': address,
                'balance': balance
            }
        }), 200
        
    except WalletError as e:
        logger.error(f"Error getting balance: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Unexpected error getting balance: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/send_transaction', methods=['POST'])
def send_transaction():
    """
    Create and process a transaction.
    
    Returns:
        JSON response with transaction details or error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        sender_address = data.get('sender_address', '').strip()
        receiver_address = data.get('receiver_address', '').strip()
        amount = float(data.get('amount', 0))
        private_key = data.get('private_key', '').strip()
        
        # Validate inputs
        if not all([sender_address, receiver_address, private_key]):
            return jsonify({
                'success': False,
                'error': 'All fields are required'
            }), 400
        
        if amount <= 0:
            return jsonify({
                'success': False,
                'error': 'Amount must be greater than 0'
            }), 400
        
        # Create transaction
        transaction = BlockchainManager.create_transaction(
            sender_address=sender_address,
            receiver_address=receiver_address,
            amount=amount,
            private_key=private_key
        )
        
        logger.info(f"Transaction created: {transaction['transaction_hash']}")
        
        # Emit WebSocket events for real-time updates
        try:
            from app.websocket_events import emit_balance_update, emit_transaction_notification
            
            # Get updated balances
            sender_wallet = WalletManager.get_wallet(sender_address)
            receiver_wallet = WalletManager.get_wallet(receiver_address)
            
            # Emit balance updates
            emit_balance_update(sender_address, sender_wallet.balance)
            emit_balance_update(receiver_address, receiver_wallet.balance)
            
            # Emit transaction notifications
            emit_transaction_notification(sender_address, transaction)
            emit_transaction_notification(receiver_address, transaction)
        except Exception as ws_error:
            # Don't fail the transaction if WebSocket fails
            logger.warning(f"WebSocket notification failed: {ws_error}")
        
        return jsonify({
            'success': True,
            'message': 'Transaction completed successfully',
            'data': transaction
        }), 201
        
    except TransactionError as e:
        logger.error(f"Transaction failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error in transaction: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/get_transactions/<address>', methods=['GET'])
def get_transactions(address):
    """
    Get transaction history for a wallet.
    
    Args:
        address (str): Wallet address
        
    Returns:
        JSON response with transaction list
    """
    try:
        # Get optional limit parameter
        limit = request.args.get('limit', type=int)
        
        # Get transactions
        transactions = BlockchainManager.get_wallet_transactions(address, limit)
        
        return jsonify({
            'success': True,
            'data': transactions
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve transactions'
        }), 500


@main_bp.route('/transactions/<address>')
def transactions_page(address):
    """
    Display all transactions for a wallet.
    
    Args:
        address (str): Wallet address
        
    Returns:
        Rendered template
    """
    try:
        wallet = WalletManager.get_wallet(address)
        transactions = BlockchainManager.get_wallet_transactions(address)
        
        return render_template(
            'transactions.html',
            wallet=wallet,
            transactions=transactions
        )
        
    except WalletError as e:
        flash(f'Wallet not found: {str(e)}', 'error')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Error loading transactions page: {e}")
        flash('An error occurred loading transactions', 'error')
        return redirect(url_for('main.index'))


@main_bp.route('/get_transaction/<tx_hash>', methods=['GET'])
def get_transaction(tx_hash):
    """
    Get details of a specific transaction.
    
    Args:
        tx_hash (str): Transaction hash
        
    Returns:
        JSON response with transaction details
    """
    try:
        transaction = BlockchainManager.get_transaction(tx_hash)
        
        if transaction:
            return jsonify({
                'success': True,
                'data': transaction
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Transaction not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting transaction: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout from wallet session.
    
    Returns:
        JSON response
    """
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


# ==================== ENHANCED FEATURES ====================

@main_bp.route('/generate_qr/<address>', methods=['GET'])
def generate_qr(address):
    """Generate QR code for wallet address."""
    try:
        qr_code = QRCodeGenerator.generate_qr_code(address)
        return jsonify({
            'success': True,
            'qr_code': qr_code
        }), 200
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate QR code'
        }), 500


@main_bp.route('/export/<address>/<format_type>', methods=['GET'])
def export_transactions(address, format_type):
    """Export transactions to CSV or PDF."""
    try:
        # Get transactions
        transactions = BlockchainManager.get_wallet_transactions(address)
        balance = WalletManager.get_balance(address)
        
        if format_type == 'csv':
            csv_data = ExportManager.export_to_csv(transactions, address)
            filename = ExportManager.generate_filename(address, 'csv')
            
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
            
        elif format_type == 'pdf':
            pdf_data = ExportManager.export_to_pdf(transactions, address, balance)
            filename = ExportManager.generate_filename(address, 'pdf')
            
            return Response(
                pdf_data,
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid format type'
            }), 400
            
    except Exception as e:
        logger.error(f"Error exporting transactions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to export transactions'
        }), 500


@main_bp.route('/enable_2fa', methods=['POST'])
def enable_2fa():
    """Enable two-factor authentication for a wallet."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        address = data.get('address', '').strip()
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'Wallet address is required'
            }), 400
        
        # Get wallet
        wallet = WalletManager.get_wallet(address)
        
        if wallet.two_factor_enabled:
            return jsonify({
                'success': False,
                'error': '2FA is already enabled for this wallet'
            }), 400
        
        # Generate secret
        secret = TwoFactorAuth.generate_secret()
        qr_code = TwoFactorAuth.generate_qr_code(secret, address)
        
        # Save secret
        wallet.two_factor_secret = secret
        wallet.two_factor_enabled = True
        db.session.commit()
        
        logger.info(f"2FA enabled for wallet: {address}")
        
        return jsonify({
            'success': True,
            'data': {
                'secret': secret,
                'qr_code': qr_code
            }
        }), 200
        
    except WalletError as e:
        db.session.rollback()
        logger.error(f"Error enabling 2FA: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error enabling 2FA: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    """Verify 2FA token."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        address = data.get('address', '').strip()
        token = data.get('token', '').strip()
        
        if not address or not token:
            return jsonify({
                'success': False,
                'error': 'Address and token are required'
            }), 400
        
        # Get wallet
        wallet = WalletManager.get_wallet(address)
        
        if not wallet.two_factor_enabled:
            return jsonify({
                'success': False,
                'error': '2FA is not enabled for this wallet'
            }), 400
        
        # Verify token
        is_valid = TwoFactorAuth.verify_token(wallet.two_factor_secret, token)
        
        return jsonify({
            'success': True,
            'valid': is_valid
        }), 200
        
    except WalletError as e:
        logger.error(f"Error verifying 2FA: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Unexpected error verifying 2FA: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@main_bp.route('/disable_2fa', methods=['POST'])
def disable_2fa():
    """Disable two-factor authentication."""
    try:
        data = request.get_json()
        address = data.get('address', '').strip()
        token = data.get('token', '').strip()
        
        if not address or not token:
            return jsonify({
                'success': False,
                'error': 'Address and token are required'
            }), 400
        
        wallet = WalletManager.get_wallet(address)
        
        # Verify token before disabling
        if not TwoFactorAuth.verify_token(wallet.two_factor_secret, token):
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        wallet.two_factor_enabled = False
        wallet.two_factor_secret = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '2FA disabled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error disabling 2FA: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/create_multisig', methods=['POST'])
def create_multisig():
    """Create a multi-signature wallet."""
    try:
        from app.multisig import MultisigManager, MultisigError
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        owners = data.get('owners', [])
        required_signatures = data.get('required_signatures', 2)
        initial_balance = Config.INITIAL_BALANCE
        
        # Create multisig wallet
        wallet = MultisigManager.create_multisig_wallet(
            owners,
            required_signatures,
            initial_balance
        )
        
        logger.info(f"Multisig wallet created: {wallet['address']}")
        
        return jsonify({
            'success': True,
            'message': 'Multi-signature wallet created successfully',
            'data': wallet
        }), 201
        
    except Exception as e:
        logger.error(f"Multisig creation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@main_bp.route('/multisig/<address>/owners', methods=['GET'])
def get_multisig_owners(address):
    """Get owners of a multisig wallet."""
    try:
        from app.multisig import MultisigManager
        
        owners = MultisigManager.get_multisig_owners(address)
        
        return jsonify({
            'success': True,
            'data': owners
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting multisig owners: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get multisig owners'
        }), 500


@main_bp.route('/multisig/<address>/pending', methods=['GET'])
def get_pending_multisig_transactions(address):
    """Get pending multisig transactions."""
    try:
        from app.multisig import MultisigManager
        
        pending = MultisigManager.get_pending_transactions(address)
        
        return jsonify({
            'success': True,
            'data': pending
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting pending transactions: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get pending transactions'
        }), 500


@main_bp.route('/exchange_rates', methods=['GET'])
def get_exchange_rates():
    """Get current exchange rates."""
    try:
        base_currency = request.args.get('base', 'COIN')
        rates = ExchangeRateManager.get_all_rates(base_currency)
        
        return jsonify({
            'success': True,
            'base_currency': base_currency,
            'rates': rates
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting exchange rates: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get exchange rates'
        }), 500


@main_bp.route('/convert', methods=['POST'])
def convert_currency():
    """Convert amount between currencies."""
    try:
        data = request.get_json()
        
        amount = float(data.get('amount', 0))
        from_currency = data.get('from_currency', 'COIN')
        to_currency = data.get('to_currency', 'USD')
        
        converted = ExchangeRateManager.convert_amount(
            amount,
            from_currency,
            to_currency
        )
        
        return jsonify({
            'success': True,
            'original_amount': amount,
            'original_currency': from_currency,
            'converted_amount': converted,
            'converted_currency': to_currency,
            'rate': ExchangeRateManager.get_rate(from_currency, to_currency)
        }), 200
        
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to convert currency'
        }), 500


@main_bp.route('/backup_wallet', methods=['POST'])
def backup_wallet():
    """Create wallet backup with mnemonic phrase."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        address = data.get('address', '').strip()
        password = data.get('password', '').strip()
        
        if not address or not password:
            return jsonify({
                'success': False,
                'error': 'Address and password are required'
            }), 400
        
        # Get wallet
        wallet = WalletManager.get_wallet(address)
        
        # Create backup
        backup = BackupManager.create_backup_data(wallet, password)
        
        # Save encrypted mnemonic to database
        wallet.backup_phrase = BackupManager.encrypt_private_key(
            backup['mnemonic'],
            password
        )
        db.session.commit()
        
        logger.info(f"Wallet backup created: {address}")
        
        return jsonify({
            'success': True,
            'message': 'Backup created successfully',
            'data': {
                'mnemonic': backup['mnemonic'],
                'encrypted_backup': backup['encrypted_backup']
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating backup: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create backup'
        }), 500


@main_bp.route('/restore_wallet', methods=['POST'])
def restore_wallet():
    """Restore wallet from mnemonic phrase."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        mnemonic = data.get('mnemonic', '').strip()
        password = data.get('password', '').strip()
        
        if not mnemonic or not password:
            return jsonify({
                'success': False,
                'error': 'Mnemonic and password are required'
            }), 400
        
        # Validate and restore
        result = BackupManager.restore_from_mnemonic(mnemonic, password)
        
        logger.info("Wallet restore validated")
        
        return jsonify({
            'success': True,
            'message': 'Mnemonic phrase is valid',
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error restoring wallet: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@main_bp.route('/refresh_exchange_rates', methods=['POST'])
def refresh_exchange_rates():
    """Manually refresh exchange rates."""
    try:
        success = ExchangeRateManager.fetch_exchange_rates()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Exchange rates updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update exchange rates'
            }), 500
            
    except Exception as e:
        logger.error(f"Error refreshing exchange rates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500