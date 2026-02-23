"""
Exchange rate management for multiple cryptocurrencies.
"""
import requests
from datetime import datetime, timedelta
from app import db
from app.models import ExchangeRate
import logging

logger = logging.getLogger(__name__)


class ExchangeRateManager:
    """Manager for cryptocurrency exchange rates."""
    
    # Supported cryptocurrencies
    SUPPORTED_CURRENCIES = ['COIN', 'BTC', 'ETH', 'USDT', 'USD']
    
    # Mock exchange rates (in production, use real API)
    MOCK_RATES = {
        ('COIN', 'USD'): 1.0,
        ('COIN', 'BTC'): 0.000025,
        ('COIN', 'ETH'): 0.0004,
        ('BTC', 'USD'): 40000.0,
        ('ETH', 'USD'): 2500.0,
        ('USDT', 'USD'): 1.0,
    }
    
    @staticmethod
    def fetch_exchange_rates():
        """
        Fetch current exchange rates from API or use mock data.
        
        Returns:
            bool: True if successful
        """
        try:
            # In production, fetch from real API
            # For now, use mock data
            for (from_curr, to_curr), rate in ExchangeRateManager.MOCK_RATES.items():
                # Check if rate exists
                existing_rate = ExchangeRate.query.filter_by(
                    from_currency=from_curr,
                    to_currency=to_curr
                ).first()
                
                if existing_rate:
                    # Update if older than 1 hour
                    if datetime.utcnow() - existing_rate.updated_at > timedelta(hours=1):
                        existing_rate.rate = rate
                        existing_rate.updated_at = datetime.utcnow()
                else:
                    # Create new rate
                    new_rate = ExchangeRate(
                        from_currency=from_curr,
                        to_currency=to_curr,
                        rate=rate
                    )
                    db.session.add(new_rate)
                
                # Also add reverse rate
                reverse_rate = ExchangeRate.query.filter_by(
                    from_currency=to_curr,
                    to_currency=from_curr
                ).first()
                
                if reverse_rate:
                    if datetime.utcnow() - reverse_rate.updated_at > timedelta(hours=1):
                        reverse_rate.rate = 1.0 / rate if rate > 0 else 0
                        reverse_rate.updated_at = datetime.utcnow()
                else:
                    new_reverse = ExchangeRate(
                        from_currency=to_curr,
                        to_currency=from_curr,
                        rate=1.0 / rate if rate > 0 else 0
                    )
                    db.session.add(new_reverse)
            
            db.session.commit()
            logger.info("Exchange rates updated successfully")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error fetching exchange rates: {e}")
            return False
    
    @staticmethod
    def get_rate(from_currency, to_currency):
        """
        Get exchange rate between two currencies.
        
        Args:
            from_currency (str): Source currency
            to_currency (str): Target currency
            
        Returns:
            float: Exchange rate
        """
        if from_currency == to_currency:
            return 1.0
        
        try:
            rate = ExchangeRate.query.filter_by(
                from_currency=from_currency,
                to_currency=to_currency
            ).first()
            
            if rate:
                return rate.rate
            
            # If not found, try to calculate via USD
            if from_currency != 'USD' and to_currency != 'USD':
                from_to_usd = ExchangeRateManager.get_rate(from_currency, 'USD')
                usd_to_to = ExchangeRateManager.get_rate('USD', to_currency)
                return from_to_usd * usd_to_to
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error getting exchange rate: {e}")
            return 1.0
    
    @staticmethod
    def convert_amount(amount, from_currency, to_currency):
        """
        Convert amount from one currency to another.
        
        Args:
            amount (float): Amount to convert
            from_currency (str): Source currency
            to_currency (str): Target currency
            
        Returns:
            float: Converted amount
        """
        rate = ExchangeRateManager.get_rate(from_currency, to_currency)
        return round(amount * rate, 8)
    
    @staticmethod
    def get_all_rates(base_currency='COIN'):
        """
        Get all exchange rates for a base currency.
        
        Args:
            base_currency (str): Base currency
            
        Returns:
            dict: Dictionary of currency: rate pairs
        """
        rates = {}
        for currency in ExchangeRateManager.SUPPORTED_CURRENCIES:
            if currency != base_currency:
                rates[currency] = ExchangeRateManager.get_rate(base_currency, currency)
        
        return rates
    
    @staticmethod
    def fetch_live_rate(from_currency, to_currency):
        """
        Fetch live exchange rate from external API.
        (Placeholder - implement with real API in production)
        
        Args:
            from_currency (str): Source currency
            to_currency (str): Target currency
            
        Returns:
            float: Exchange rate or None
        """
        # Example: CoinGecko API integration
        # try:
        #     response = requests.get(
        #         f'https://api.coingecko.com/api/v3/simple/price',
        #         params={'ids': from_currency, 'vs_currencies': to_currency}
        #     )
        #     data = response.json()
        #     return data[from_currency][to_currency]
        # except:
        #     return None
        
        # For now, return mock data
        pair = (from_currency, to_currency)
        return ExchangeRateManager.MOCK_RATES.get(pair)