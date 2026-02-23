"""
Export utility for transaction history (CSV and PDF).
"""
import csv
from io import StringIO, BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import logging

logger = logging.getLogger(__name__)


class ExportManager:
    """Manager for exporting transaction data to various formats."""
    
    @staticmethod
    def export_to_csv(transactions, wallet_address):
        """
        Export transactions to CSV format.
        
        Args:
            transactions (list): List of transaction dictionaries
            wallet_address (str): Wallet address for the export
            
        Returns:
            str: CSV string
        """
        try:
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Date',
                'Type',
                'From',
                'To',
                'Amount',
                'Transaction Hash',
                'Status'
            ])
            
            # Write transaction data
            for tx in transactions:
                tx_type = 'Received' if tx['receiver_address'] == wallet_address else 'Sent'
                
                writer.writerow([
                    tx['timestamp'],
                    tx_type,
                    tx['sender_address'],
                    tx['receiver_address'],
                    tx['amount'],
                    tx['transaction_hash'],
                    tx['status']
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    @staticmethod
    def export_to_pdf(transactions, wallet_address, wallet_balance):
        """
        Export transactions to PDF format.
        
        Args:
            transactions (list): List of transaction dictionaries
            wallet_address (str): Wallet address
            wallet_balance (float): Current wallet balance
            
        Returns:
            bytes: PDF file as bytes
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#4f46e5'),
                spaceAfter=30,
            )
            
            # Title
            title = Paragraph("Transaction History Report", title_style)
            elements.append(title)
            
            # Wallet info
            wallet_info = [
                ['Wallet Address:', wallet_address],
                ['Current Balance:', f'{wallet_balance} coins'],
                ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Total Transactions:', str(len(transactions))]
            ]
            
            wallet_table = Table(wallet_info, colWidths=[2*inch, 4*inch])
            wallet_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(wallet_table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Transaction table
            if transactions:
                # Table header
                data = [['Date', 'Type', 'Amount', 'Hash', 'Status']]
                
                # Table data
                for tx in transactions:
                    tx_type = 'Received' if tx['receiver_address'] == wallet_address else 'Sent'
                    tx_hash_short = tx['transaction_hash'][:16] + '...'
                    
                    data.append([
                        datetime.fromisoformat(tx['timestamp']).strftime('%Y-%m-%d %H:%M'),
                        tx_type,
                        f"{'+' if tx_type == 'Received' else '-'}{tx['amount']}",
                        tx_hash_short,
                        tx['status'].upper()
                    ])
                
                # Create table
                tx_table = Table(data, colWidths=[1.5*inch, 1*inch, 1*inch, 2*inch, 1*inch])
                tx_table.setStyle(TableStyle([
                    # Header
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    # Body
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                elements.append(tx_table)
            else:
                no_tx = Paragraph("No transactions found.", styles['Normal'])
                elements.append(no_tx)
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise
    
    @staticmethod
    def generate_filename(wallet_address, format_type):
        """
        Generate filename for export.
        
        Args:
            wallet_address (str): Wallet address
            format_type (str): 'csv' or 'pdf'
            
        Returns:
            str: Filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        address_short = wallet_address[:10]
        return f"transactions_{address_short}_{timestamp}.{format_type}"