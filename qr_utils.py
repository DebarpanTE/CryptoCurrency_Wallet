"""
QR Code generation utility for wallet addresses.
"""
import qrcode
from io import BytesIO
import base64
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class QRCodeGenerator:
    """Utility class for generating QR codes for wallet addresses."""
    
    @staticmethod
    def generate_qr_code(data, size=300):
        """
        Generate a QR code for wallet address or transaction data.
        
        Args:
            data (str): Data to encode (wallet address, payment URI, etc.)
            size (int): Size of the QR code in pixels
            
        Returns:
            str: Base64 encoded PNG image
            
        Raises:
            Exception: If QR code generation fails
        """
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add data
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize if needed
            if size != 300:
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise
    
    @staticmethod
    def generate_payment_qr(address, amount=None, label=None):
        """
        Generate a QR code for a payment request.
        
        Args:
            address (str): Wallet address
            amount (float, optional): Payment amount
            label (str, optional): Payment label/description
            
        Returns:
            str: Base64 encoded QR code image
        """
        # Create payment URI
        uri = f"crypto:{address}"
        
        params = []
        if amount:
            params.append(f"amount={amount}")
        if label:
            params.append(f"label={label}")
        
        if params:
            uri += "?" + "&".join(params)
        
        return QRCodeGenerator.generate_qr_code(uri)
    
    @staticmethod
    def save_qr_code(data, filepath):
        """
        Save QR code to file.
        
        Args:
            data (str): Data to encode
            filepath (str): Path to save the QR code image
            
        Returns:
            bool: True if successful
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filepath)
            
            logger.info(f"QR code saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving QR code: {e}")
            return False