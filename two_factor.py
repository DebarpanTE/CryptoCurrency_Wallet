"""
Two-Factor Authentication (2FA) utility using TOTP.
"""
import pyotp
import qrcode
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)


class TwoFactorAuth:
    """Two-Factor Authentication manager using Time-based OTP."""
    
    @staticmethod
    def generate_secret():
        """
        Generate a new TOTP secret.
        
        Returns:
            str: Base32 encoded secret
        """
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret, account_name, issuer_name="CryptoWallet"):
        """
        Generate TOTP provisioning URI.
        
        Args:
            secret (str): TOTP secret
            account_name (str): Account name (wallet address)
            issuer_name (str): Issuer name
            
        Returns:
            str: TOTP URI for QR code generation
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=account_name,
            issuer_name=issuer_name
        )
    
    @staticmethod
    def generate_qr_code(secret, account_name):
        """
        Generate QR code for 2FA setup.
        
        Args:
            secret (str): TOTP secret
            account_name (str): Account name (wallet address)
            
        Returns:
            str: Base64 encoded QR code image
        """
        try:
            uri = TwoFactorAuth.get_totp_uri(secret, account_name)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating 2FA QR code: {e}")
            raise
    
    @staticmethod
    def verify_token(secret, token):
        """
        Verify a TOTP token.
        
        Args:
            secret (str): TOTP secret
            token (str): 6-digit token from authenticator app
            
        Returns:
            bool: True if token is valid
        """
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False
    
    @staticmethod
    def get_current_token(secret):
        """
        Get current TOTP token (for testing).
        
        Args:
            secret (str): TOTP secret
            
        Returns:
            str: Current 6-digit token
        """
        totp = pyotp.TOTP(secret)
        return totp.now()