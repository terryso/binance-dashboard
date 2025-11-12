import streamlit as st
import toml
from pathlib import Path
from typing import Dict, Any

from config.settings import load_config, save_config
from config.secrets import SecretsManager
from binance_api.client import BinanceClient

def show_settings():
    """Display settings page"""
    st.title("⚙️ Settings & Configuration")
    st.markdown("---")

    # Load current config
    config = load_config()

    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs(["🔑 API Configuration", "🎨 Display Settings", "📊 App Settings", "ℹ️ System Info"])

    with tab1:
        st.markdown("### 🔑 Binance API Configuration")

        # API Credentials
        st.markdown("#### API Credentials")

        # Current credentials status
        api_key = SecretsManager.get_api_key()
        secret_key = SecretsManager.get_secret_key()

        if api_key and secret_key:
            st.success("✅ API credentials are configured")
        else:
            st.warning("⚠️ API credentials not found")

        # Manual credential input
        with st.expander("🔧 Configure API Credentials"):
            st.markdown("**Note:** Credentials are stored temporarily in session state for security.")

            manual_api_key = st.text_input(
                "API Key",
                value="",
                type="password",
                help="Your Binance Futures API Key"
            )

            manual_secret_key = st.text_input(
                "Secret Key",
                value="",
                type="password",
                help="Your Binance Futures Secret Key"
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Save Credentials", type="primary"):
                    if manual_api_key and manual_secret_key:
                        if SecretsManager.validate_credentials(manual_api_key, manual_secret_key):
                            SecretsManager.store_temp_credentials(manual_api_key, manual_secret_key)
                            st.success("✅ Credentials saved successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials format")
                    else:
                        st.error("❌ Please enter both API key and secret key")

            with col2:
                if st.button("🗑️ Clear Credentials"):
                    SecretsManager.clear_temp_credentials()
                    st.success("✅ Credentials cleared!")
                    st.rerun()

        # Test connection
        st.markdown("#### Test API Connection")
        if st.button("🔗 Test Connection"):
            with st.spinner("Testing connection..."):
                try:
                    # Get temporary credentials if available
                    temp_key, temp_secret = SecretsManager.get_temp_credentials()
                    if temp_key and temp_secret:
                        test_config = config.copy()
                        test_config['binance']['api_key'] = temp_key
                        test_config['binance']['secret_key'] = temp_secret

                        test_client = BinanceClient(test_config)
                        if test_client.test_connection():
                            st.success("✅ Connection successful!")
                            # Show account info preview
                            account_info = test_client.get_account_info()
                            st.info(f"Connected! Total balance: ${account_info.get('total_balance', 0):,.2f}")
                        else:
                            st.error("❌ Connection failed")
                    else:
                        st.error("❌ No credentials configured")

                except Exception as e:
                    st.error(f"❌ Connection error: {e}")

        # Environment setup
        st.markdown("#### Environment Setup")
        use_testnet = st.checkbox(
            "🧪 Use Testnet",
            value=config.get('binance', {}).get('use_testnet', False),
            help="Use Binance Testnet for testing (requires separate testnet API keys)"
        )

        api_timeout = st.number_input(
            "⏱️ API Timeout (seconds)",
            min_value=5,
            max_value=120,
            value=config.get('binance', {}).get('timeout', 30),
            help="Timeout for API requests"
        )

    with tab2:
        st.markdown("### 🎨 Display Settings")

        # Theme settings
        st.markdown("#### Theme Configuration")
        theme = st.selectbox(
            "🎨 Color Theme",
            ["dark", "light"],
            index=0 if config.get('app', {}).get('theme') == 'dark' else 1,
            help="Choose application theme"
        )

        # Currency settings
        st.markdown("#### Currency Settings")
        default_currency = st.selectbox(
            "💱 Default Currency",
            ["USDT", "BUSD", "BTC"],
            index=0 if config.get('display', {}).get('default_currency') == 'USDT' else 1,
            help="Default currency for displaying values"
        )

        # Date/Time settings
        st.markdown("#### Date & Time Settings")
        timezone = st.selectbox(
            "🌍 Timezone",
            ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo", "Asia/Shanghai"],
            index=0,
            help="Timezone for displaying timestamps"
        )

        date_format = st.selectbox(
            "📅 Date Format",
            ["%Y-%m-%d %H:%M:%S", "%m/%d/%Y %I:%M:%S %p", "%d/%m/%Y %H:%M:%S"],
            index=0,
            help="Format for displaying dates and times"
        )

        # Refresh settings
        refresh_interval = st.number_input(
            "🔄 Refresh Interval (seconds)",
            min_value=10,
            max_value=300,
            value=config.get('app', {}).get('refresh_interval', 60),
            help="How often to refresh data from API"
        )

    with tab3:
        st.markdown("### 📊 Application Settings")

        # Performance settings
        st.markdown("#### Performance Settings")
        enable_cache = st.checkbox(
            "💾 Enable Data Caching",
            value=True,
            help="Cache API responses to reduce rate limiting"
        )

        cache_timeout = st.number_input(
            "⏰ Cache Timeout (seconds)",
            min_value=30,
            max_value=600,
            value=60,
            help="How long to keep cached data"
        )

        # Data display settings
        st.markdown("#### Data Display Settings")
        max_records = st.number_input(
            "📋 Maximum Records to Display",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Maximum number of records to show in tables"
        )

        decimal_places = st.number_input(
            "🔢 Decimal Places",
            min_value=2,
            max_value=8,
            value=4,
            help="Number of decimal places to display for prices"
        )

        # Risk settings
        st.markdown("#### Risk Management")
        leverage_warning = st.number_input(
            "⚠️ High Leverage Warning Threshold",
            min_value=2,
            max_value=50,
            value=10,
            help="Show warning when leverage exceeds this value"
        )

        position_size_warning = st.number_input(
            "💸 Large Position Warning (USDT)",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000,
            help="Show warning when position size exceeds this amount"
        )

    with tab4:
        st.markdown("### ℹ️ System Information")

        st.markdown("#### 📦 Package Information")
        st.info("""
        **Binance Futures Dashboard**
        Version: 1.0.0
        Framework: Streamlit
        API: Binance Futures API

        **Dependencies:**
        - streamlit>=1.28.0
        - python-binance>=1.0.19
        - pandas>=2.0.0
        - plotly>=5.15.0
        """)

        st.markdown("#### 🔗 API Endpoints")
        if use_testnet:
            st.code("Binance Futures Testnet: https://testnet.binancefuture.com")
        else:
            st.code("Binance Futures: https://fapi.binance.com")

        st.markdown("#### 📁 Configuration Files")
        config_files = [
            "config.toml - Main configuration",
            ".env - Environment variables",
            "requirements.txt - Python dependencies"
        ]

        for file_info in config_files:
            st.write(f"• {file_info}")

        st.markdown("#### 🛡️ Security Notes")
        st.warning("""
        • API credentials are stored temporarily in session state
        • Never share your API keys or secrets
        • Use API keys with limited permissions when possible
        • Consider using IP whitelist for your API keys
        • Enable testnet mode for development and testing
        """)

    # Save configuration button
    st.markdown("---")
    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("💾 Save Settings", type="primary"):
            # Update config with new values
            updated_config = config.copy()

            # Update binance settings
            updated_config['binance']['use_testnet'] = use_testnet
            updated_config['binance']['timeout'] = api_timeout

            # Update app settings
            updated_config['app']['theme'] = theme
            updated_config['app']['refresh_interval'] = refresh_interval

            # Update display settings
            updated_config['display']['default_currency'] = default_currency
            updated_config['display']['timezone'] = timezone
            updated_config['display']['date_format'] = date_format

            if save_config(updated_config):
                st.success("✅ Settings saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save settings")

    with col2:
        st.markdown("*Settings are saved to `config.toml` file. API credentials are stored in session state for security.*")

    # Configuration preview
    st.markdown("---")
    st.markdown("### 📋 Current Configuration Preview")

    # Create safe config display (without sensitive data)
    safe_config = config.copy()
    if 'api_key' in safe_config.get('binance', {}):
        del safe_config['binance']['api_key']
    if 'secret_key' in safe_config.get('binance', {}):
        del safe_config['binance']['secret_key']

    st.json(safe_config)