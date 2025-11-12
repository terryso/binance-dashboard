"""Secure management of API keys and sensitive information"""

import os
import streamlit as st
from typing import Optional

class SecretsManager:
    """Manages sensitive configuration securely"""

    @staticmethod
    def get_api_key() -> Optional[str]:
        """Get Binance API key from secure storage"""
        # Try Streamlit secrets first (for deployment)
        if hasattr(st, 'secrets') and 'BINANCE_API_KEY' in st.secrets:
            return st.secrets['BINANCE_API_KEY']

        # Fall back to environment variables
        return os.getenv('BINANCE_API_KEY')

    @staticmethod
    def get_secret_key() -> Optional[str]:
        """Get Binance secret key from secure storage"""
        # Try Streamlit secrets first (for deployment)
        if hasattr(st, 'secrets') and 'BINANCE_SECRET_KEY' in st.secrets:
            return st.secrets['BINANCE_SECRET_KEY']

        # Fall back to environment variables
        return os.getenv('BINANCE_SECRET_KEY')

    @staticmethod
    def validate_credentials(api_key: str, secret_key: str) -> bool:
        """Validate that credentials are properly formatted"""
        if not api_key or not secret_key:
            return False

        # Basic validation - API keys are typically 64 characters
        if len(api_key) < 20 or len(secret_key) < 20:
            return False

        return True

    @staticmethod
    def store_temp_credentials(api_key: str, secret_key: str) -> bool:
        """Store credentials temporarily in session state"""
        if not SecretsManager.validate_credentials(api_key, secret_key):
            return False

        st.session_state['temp_api_key'] = api_key
        st.session_state['temp_secret_key'] = secret_key
        return True

    @staticmethod
    def get_temp_credentials() -> tuple[Optional[str], Optional[str]]:
        """Get temporarily stored credentials"""
        api_key = st.session_state.get('temp_api_key')
        secret_key = st.session_state.get('temp_secret_key')
        return api_key, secret_key

    @staticmethod
    def clear_temp_credentials():
        """Clear temporarily stored credentials"""
        if 'temp_api_key' in st.session_state:
            del st.session_state['temp_api_key']
        if 'temp_secret_key' in st.session_state:
            del st.session_state['temp_secret_key']