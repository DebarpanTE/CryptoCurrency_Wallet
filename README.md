# Cryptocurrency Wallet Application

A basic cryptocurrency wallet application built with Python and Flask that allows users to manage their cryptocurrency holdings.

## Features

- 🔐 Secure wallet creation with private/public key pairs
- 💰 Check wallet balance
- 📤 Send cryptocurrency to other wallets
- 📥 Receive cryptocurrency
- 📊 View transaction history
- 🔍 Transaction validation
- 💾 Persistent storage using SQLite

## Project Structure

```
crypto-wallet/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── models.py             # Database models
│   ├── blockchain.py         # Blockchain and transaction logic
│   ├── wallet.py             # Wallet management
│   ├── routes.py             # API routes
│   └── templates/            # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── wallet.html
│       └── transactions.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── tests/
│   ├── __init__.py
│   └── test_wallet.py
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
└── README.md                 # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Navigate to Project Directory

```bash
cd cryptocurrency_project
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

Or simply run the application (it will auto-create tables):

```bash
python run.py
```

### Step 5: Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

## Usage Guide

### 1. Create a Wallet

- Click "Create New Wallet" on the homepage
- Save your private key securely (you'll need it to access your wallet)
- Your public address will be displayed

### 2. Access Your Wallet

- Enter your private key on the homepage
- Click "Access Wallet"

### 3. Send Cryptocurrency

- Navigate to your wallet dashboard
- Enter recipient's address
- Enter amount to send
- Click "Send"

### 4. Receive Cryptocurrency

- Share your public address with the sender
- Transactions will appear in your wallet automatically

### 5. View Transactions

- All transactions (sent and received) are displayed in the transaction history
- Each transaction shows: sender, receiver, amount, timestamp, and hash

## API Endpoints

### Wallet Management

- `GET /` - Home page
- `POST /create_wallet` - Create a new wallet
- `POST /access_wallet` - Access existing wallet
- `GET /wallet/<address>` - View wallet details

### Transactions

- `POST /send_transaction` - Send cryptocurrency
- `GET /transactions/<address>` - Get transaction history
- `GET /balance/<address>` - Get wallet balance

## Security Notes

⚠️ **Important Security Warnings:**

1. **Private Keys**: Never share your private key. Store it securely offline.
2. **Development Only**: This is a demonstration project. Do NOT use for real cryptocurrency.
3. **No Real Value**: This wallet manages fictional cryptocurrency for educational purposes.
4. **Encryption**: In production, implement proper encryption for private keys.
5. **HTTPS**: Always use HTTPS in production environments.

## Technical Details

### Blockchain Implementation

- Uses SHA-256 hashing for transactions
- Each transaction contains: sender, receiver, amount, timestamp
- Transactions are validated before execution
- Balance verification prevents double-spending

### Database Schema

**Wallets Table:**

- `id` (Primary Key)
- `address` (Unique, indexed)
- `private_key` (Hashed)
- `balance` (Decimal)
- `created_at` (Timestamp)

**Transactions Table:**

- `id` (Primary Key)
- `sender_address`
- `receiver_address`
- `amount`
- `timestamp`
- `transaction_hash` (Unique)

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run specific tests:

```bash
python -m pytest tests/test_wallet.py -v
```

## Troubleshooting

### Database Errors

If you encounter database errors:

```bash
rm instance/wallet.db
python run.py
```

### Port Already in Use

Change the port in `run.py`:

```python
app.run(debug=True, port=5001)  # Changed from 5000
```

### Module Not Found Errors

Ensure virtual environment is activated and dependencies are installed:

```bash
pip install -r requirements.txt
```

## Future Enhancements

- [ ] Multi-signature wallets
- [ ] QR code generation for addresses
- [ ] Export transaction history (CSV/PDF)
- [ ] Real-time balance updates (WebSockets)
- [ ] Multiple cryptocurrency support
- [ ] Exchange rate integration
- [ ] Two-factor authentication
- [ ] Wallet backup/restore functionality

## Contributing

This is an educational project. Feel free to fork and extend!

## License

MIT License - See LICENSE file for details

## Disclaimer

This application is for educational purposes only. It does not interact with any real blockchain network and manages fictional cryptocurrency. Do not use this for real financial transactions.