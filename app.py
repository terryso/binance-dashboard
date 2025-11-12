import streamlit as st
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import load_config
from binance_api.client import BinanceClient
from ui.pages.dashboard import show_dashboard
from ui.pages.positions import show_positions
from ui.pages.history import show_history
from ui.pages.settings import show_settings

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Binance Futures Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load configuration
    config = load_config()

    # Initialize session state
    if 'client' not in st.session_state:
        try:
            st.session_state.client = BinanceClient(config)
        except Exception as e:
            st.error(f"Failed to initialize Binance client: {e}")
            st.session_state.client = None

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Sidebar navigation
    with st.sidebar:
        st.title("📊 Binance Dashboard")
        st.markdown("---")

        # Navigation
        pages = ["Dashboard", "Positions", "History", "Settings"]
        page = st.selectbox("Navigation", pages, index=pages.index(st.session_state.current_page))
        st.session_state.current_page = page

        st.markdown("---")

        # Connection status
        if st.session_state.client:
            try:
                account_info = st.session_state.client.get_account_info()
                st.success("✅ Connected")
                st.markdown(f"**Total Balance:** ${account_info.get('total_balance', 0):,.2f}")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")
        else:
            st.error("❌ Not Connected")

    # Page routing
    try:
        if page == "Dashboard":
            show_dashboard()
        elif page == "Positions":
            show_positions()
        elif page == "History":
            show_history()
        elif page == "Settings":
            show_settings()
    except Exception as e:
        st.error(f"Error loading page: {e}")
        st.markdown("Please check your API configuration in the Settings page.")

if __name__ == "__main__":
    main()