"""
WebSocket events for real-time balance and transaction updates.
"""
from flask_socketio import emit, join_room, leave_room
from app import socketio
import logging

logger = logging.getLogger(__name__)


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    emit('connected', {'data': 'Connected to CryptoWallet'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')


@socketio.on('subscribe_wallet')
def handle_subscribe_wallet(data):
    """
    Subscribe to wallet updates.
    
    Args:
        data (dict): {'wallet_address': 'address'}
    """
    try:
        wallet_address = data.get('wallet_address')
        if wallet_address:
            join_room(wallet_address)
            logger.info(f"Client subscribed to wallet: {wallet_address}")
            emit('subscribed', {'wallet_address': wallet_address})
    except Exception as e:
        logger.error(f"Error subscribing to wallet: {e}")
        emit('error', {'message': 'Failed to subscribe to wallet'})


@socketio.on('unsubscribe_wallet')
def handle_unsubscribe_wallet(data):
    """
    Unsubscribe from wallet updates.
    
    Args:
        data (dict): {'wallet_address': 'address'}
    """
    try:
        wallet_address = data.get('wallet_address')
        if wallet_address:
            leave_room(wallet_address)
            logger.info(f"Client unsubscribed from wallet: {wallet_address}")
            emit('unsubscribed', {'wallet_address': wallet_address})
    except Exception as e:
        logger.error(f"Error unsubscribing from wallet: {e}")


def emit_balance_update(wallet_address, new_balance):
    """
    Emit balance update to subscribed clients.
    
    Args:
        wallet_address (str): Wallet address
        new_balance (float): New balance
    """
    try:
        socketio.emit(
            'balance_updated',
            {
                'wallet_address': wallet_address,
                'balance': new_balance
            },
            room=wallet_address
        )
        logger.info(f"Balance update emitted for {wallet_address}: {new_balance}")
    except Exception as e:
        logger.error(f"Error emitting balance update: {e}")


def emit_transaction_notification(wallet_address, transaction_data):
    """
    Emit transaction notification to subscribed clients.
    
    Args:
        wallet_address (str): Wallet address
        transaction_data (dict): Transaction details
    """
    try:
        socketio.emit(
            'new_transaction',
            {
                'wallet_address': wallet_address,
                'transaction': transaction_data
            },
            room=wallet_address
        )
        logger.info(f"Transaction notification emitted for {wallet_address}")
    except Exception as e:
        logger.error(f"Error emitting transaction notification: {e}")


def emit_exchange_rate_update(from_currency, to_currency, rate):
    """
    Emit exchange rate update to all connected clients.
    
    Args:
        from_currency (str): Source currency
        to_currency (str): Target currency
        rate (float): Exchange rate
    """
    try:
        socketio.emit(
            'exchange_rate_updated',
            {
                'from_currency': from_currency,
                'to_currency': to_currency,
                'rate': rate
            },
            broadcast=True
        )
        logger.info(f"Exchange rate update emitted: {from_currency}/{to_currency} = {rate}")
    except Exception as e:
        logger.error(f"Error emitting exchange rate update: {e}")