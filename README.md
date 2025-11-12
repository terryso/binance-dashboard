# Binance Futures Dashboard

A modern, real-time dashboard for monitoring Binance Futures trading accounts built with Streamlit.

## 🚀 Features

- **Real-time Account Monitoring**: Track account balance, P&L, and position details
- **Interactive Charts**: Visualize trading performance with Plotly charts
- **Position Management**: Monitor active positions with risk analysis
- **Transaction History**: Analyze past trades and income records
- **Secure API Integration**: Safe handling of Binance API credentials
- **Responsive Design**: Mobile-friendly interface
- **Data Caching**: Efficient API usage with intelligent caching
- **Export Functionality**: Download trading data in CSV format

## 📋 Requirements

- Python 3.8+
- Binance Futures Account with API access

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd binance-dashboard
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Credentials

#### Option A: Environment Variables (Recommended)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your Binance API credentials:
```env
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
USE_TESTNET=false
REFRESH_INTERVAL=60
```

#### Option B: In-App Configuration

You can also configure API credentials directly in the application's Settings page.

### 5. Run the Application

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 🔧 Configuration

### Binance API Setup

1. Log in to your Binance account
2. Navigate to **API Management** in your account settings
3. Create a new API key with the following permissions:
   - **Enable Reading**: Required for account information
   - **Enable Futures**: Required for futures trading data
   - **Enable Spot & Margin Trading**: Not required, can be disabled for security
4. Set up IP restrictions (recommended for security)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BINANCE_API_KEY` | Your Binance API key | Required |
| `BINANCE_SECRET_KEY` | Your Binance secret key | Required |
| `USE_TESTNET` | Use testnet environment | `false` |
| `REFRESH_INTERVAL` | Data refresh interval in seconds | `60` |
| `APP_THEME` | Application theme | `dark` |
| `DEFAULT_CURRENCY` | Default display currency | `USDT` |

### Configuration File

You can also configure the application using `config.toml`:

```toml
[app]
name = "Binance Futures Dashboard"
refresh_interval = 60
theme = "dark"

[binance]
use_testnet = false
timeout = 30

[display]
default_currency = "USDT"
timezone = "UTC"
date_format = "%Y-%m-%d %H:%M:%S"
```

## 📱 Usage Guide

### Dashboard Overview

The main dashboard provides:

- **Account Summary**: Total balance, available balance, P&L, and leverage usage
- **Asset Distribution**: Visual breakdown of your portfolio
- **Position P&L**: Real-time profit and loss for active positions
- **Active Positions Table**: Detailed view of all open positions

### Positions Page

- **Filter Positions**: Filter by side (LONG/SHORT), P&L status, and leverage
- **Risk Analysis**: View position risk metrics and leverage usage
- **Position Details**: Entry price, mark price, size, and P&L information
- **Export Data**: Download position data as CSV

### Transaction History

- **Time Period Selection**: View trades for different time periods
- **Symbol Filtering**: Filter transactions by specific trading pairs
- **Trading Statistics**: Volume, commission, and trade count analysis
- **Income Tracking**: View funding fees, rebates, and other income sources

### Settings Configuration

- **API Configuration**: Set up and test Binance API credentials
- **Display Settings**: Customize theme, currency, and time formats
- **Performance Settings**: Configure caching and data limits
- **Risk Management**: Set warning thresholds for leverage and position size

## 🔒 Security Features

- **Secure Credential Storage**: API keys stored in session state, not in files
- **Environment Variable Support**: Recommended method for production deployments
- **Permission Control**: Minimal required API permissions
- **Testnet Support**: Safe testing environment available
- **IP Whitelist**: Compatible with Binance IP restrictions

## 📊 API Limits and Caching

The application implements intelligent caching to respect Binance API rate limits:

- **Account Data**: Cached for 30 seconds
- **Transaction History**: Cached for 60 seconds
- **Income History**: Cached for 5 minutes
- **Configurable Timeouts**: Adjust cache durations in settings

## 🚀 Deployment

### Streamlit Cloud (Recommended)

1. Push your code to a GitHub repository
2. Create a new app on [Streamlit Cloud](https://share.streamlit.io/)
3. Configure secrets in the deployment settings:
   - `BINANCE_API_KEY`: Your API key
   - `BINANCE_SECRET_KEY`: Your secret key

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Manual Deployment

```bash
# Set environment variables
export BINANCE_API_KEY="your_key"
export BINANCE_SECRET_KEY="your_secret"

# Run the app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 🛠️ Development

### Project Structure

```
binance-dashboard/
├── app.py                 # Main Streamlit application
├── config/                # Configuration management
│   ├── settings.py        # Configuration loading/saving
│   └── secrets.py         # Secure credential management
├── binance/               # Binance API integration
│   ├── client.py          # API client wrapper
│   ├── models.py          # Data models
│   └── utils.py           # Utility functions
├── ui/                    # User interface components
│   ├── pages/             # Streamlit pages
│   ├── components/        # Reusable UI components
│   └── charts/            # Chart components
├── data/                  # Data processing
│   ├── processor.py       # Data analysis and processing
│   └── cache.py           # Caching system
├── tests/                 # Test files
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── config.toml           # Application configuration
└── .env                  # Environment variables (not in git)
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=binance tests/
```

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **Type hints** for better code documentation

```bash
# Format code
black .

# Lint code
flake8 .
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for informational purposes only. The authors are not responsible for any financial losses or damages. Trading cryptocurrencies involves substantial risk of loss and is not suitable for all investors.

## 🆘 Support

If you encounter issues:

1. Check the [FAQ](docs/FAQ.md)
2. Review existing [GitHub Issues](https://github.com/your-repo/issues)
3. Create a new issue with detailed information

## 📚 Additional Resources

- [Binance Futures API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Python-Binance Library](https://python-binance.readthedocs.io/)