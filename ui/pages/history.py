import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from data.processor import DataProcessor
from data.cache import get_cached_api
from binance_api.utils import format_currency, format_percentage, get_date_range_preset

def show_history():
    """Display transaction history page"""
    st.title("📜 Transaction History")
    st.markdown("---")

    # Initialize data processor
    processor = DataProcessor()
    cached_api = get_cached_api()

    # Get client from session state
    client = st.session_state.get('client')

    if not client:
        st.error("❌ Not connected to Binance API")
        st.info("Please configure your API credentials in the Settings page.")
        return

    # Sidebar controls
    st.sidebar.markdown("### 🔍 Filters & Settings")

    # Date range selection
    date_options = {
        "Last 7 days": 7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 6 months": 180,
        "Last year": 365
    }

    selected_period = st.sidebar.selectbox("Time Period", list(date_options.keys()))
    days = date_options[selected_period]

    # Symbol filter (optional)
    symbol_filter = st.sidebar.text_input("Symbol Filter (optional)", placeholder="BTCUSDT")

    # Transaction type filter
    transaction_types = ['All', 'BUY', 'SELL']
    selected_type = st.sidebar.selectbox("Transaction Type", transaction_types)

    # Number of records
    limit = st.sidebar.slider("Number of Records", 10, 500, 100)

    # Load data with filters
    with st.spinner("Loading transaction history..."):
        try:
            trades_df = cached_api.cached_transaction_history(
                client,
                symbol=symbol_filter if symbol_filter else None,
                limit=limit
            )

            income_df = cached_api.cached_income_history(
                client,
                symbol=symbol_filter if symbol_filter else None,
                limit=limit
            )

        except Exception as e:
            st.error(f"❌ Error loading transaction history: {e}")
            return

    # Process data
    if not trades_df.empty:
        # Apply filters
        filtered_trades = trades_df.copy()

        # Date filter
        cutoff_date = datetime.now() - timedelta(days=days)
        if 'time' in filtered_trades.columns:
            filtered_trades = filtered_trades[filtered_trades['time'] >= cutoff_date]

        # Transaction type filter
        if selected_type != 'All' and 'side' in filtered_trades.columns:
            filtered_trades = filtered_trades[filtered_trades['side'] == selected_type]

        # Symbol filter (if not already applied in API call)
        if symbol_filter and 'symbol' in filtered_trades.columns:
            filtered_trades = filtered_trades[filtered_trades['symbol'] == symbol_filter]

        # Process trades data
        trades_analysis = processor.process_trades_data(filtered_trades)

        # Summary metrics
        st.markdown("### 📊 Trading Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Trades",
                f"{trades_analysis['total_trades']:,}",
                help="Total number of completed trades"
            )

        with col2:
            st.metric(
                "Total Volume",
                format_currency(trades_analysis['total_volume']),
                help="Total trading volume in USDT"
            )

        with col3:
            st.metric(
                "Total Commission",
                format_currency(trades_analysis['total_commission']),
                help="Total fees paid to exchange"
            )

        with col4:
            st.metric(
                "Avg Trade Size",
                f"{trades_analysis['avg_trade_size']:.4f}",
                help="Average trade size in base currency"
            )

        st.markdown("---")

        # Visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Daily Trading Volume")
            if not trades_analysis['trades_by_day'].empty:
                daily_df = trades_analysis['trades_by_day'].reset_index()
                daily_df['date'] = pd.to_datetime(daily_df['date'])

                fig = px.line(
                    daily_df,
                    x='date',
                    y='quoteQty',
                    title='Daily Trading Volume',
                    labels={'quoteQty': 'Volume (USDT)', 'date': 'Date'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No daily volume data available")

        with col2:
            st.subheader("🏆 Most Traded Symbols")
            if trades_analysis['trades_by_symbol']:
                symbol_df = pd.DataFrame(trades_analysis['trades_by_symbol']).T.reset_index()
                symbol_df.columns = ['Symbol', 'Trade Count', 'Volume', 'Commission']

                # Sort by volume and take top 10
                symbol_df = symbol_df.nlargest(10, 'Volume')

                fig = px.bar(
                    symbol_df,
                    x='Symbol',
                    y='Volume',
                    title='Top Traded Symbols by Volume',
                    labels={'Volume': 'Volume (USDT)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No symbol trading data available")

        st.markdown("---")

        # Detailed transactions table
        st.subheader("📋 Transaction History")

        if not filtered_trades.empty:
            # Prepare display data
            display_df = filtered_trades.copy()

            # Format columns for display
            if 'price' in display_df.columns:
                display_df['price'] = display_df['price'].round(4)

            if 'qty' in display_df.columns:
                display_df['qty'] = display_df['qty'].round(4)

            if 'quoteQty' in display_df.columns:
                display_df['quoteQty'] = display_df['quoteQty'].round(2)

            if 'commission' in display_df.columns:
                display_df['commission'] = display_df['commission'].round(4)

            if 'realized_pnl' in display_df.columns:
                display_df['realized_pnl'] = display_df['realized_pnl'].round(2)

            # Select and rename columns for display
            if 'time' in display_df.columns:
                display_df['time'] = pd.to_datetime(display_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')

            display_columns = ['time', 'symbol', 'side', 'qty', 'price', 'quoteQty', 'commission', 'realized_pnl']
            available_columns = [col for col in display_columns if col in display_df.columns]

            if available_columns:
                display_data = display_df[available_columns].copy()
                column_mapping = {
                    'time': 'Time',
                    'symbol': 'Symbol',
                    'side': 'Side',
                    'qty': 'Quantity',
                    'price': 'Price',
                    'quoteQty': 'Total',
                    'commission': 'Commission',
                    'realized_pnl': 'Realized P&L'
                }

                display_data.columns = [column_mapping.get(col, col) for col in display_data.columns]

                st.dataframe(
                    display_data,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
        else:
            st.info("No transactions match the current filters")

    else:
        st.info("No transaction history found")

    # Income/Fees Analysis
    if not income_df.empty:
        st.markdown("---")
        st.subheader("💰 Income & Fees History")

        # Apply date filter
        filtered_income = income_df.copy()
        cutoff_date = datetime.now() - timedelta(days=days)
        if 'time' in filtered_income.columns:
            filtered_income['time'] = pd.to_datetime(filtered_income['time'])
            filtered_income = filtered_income[filtered_income['time'] >= cutoff_date]

        if not filtered_income.empty:
            # Process income data
            income_analysis = processor.process_income_data(filtered_income)

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Total Income",
                    format_currency(income_analysis['total_income']),
                    help="Total income from all sources"
                )

                # Income by type breakdown
                if income_analysis['income_by_type']:
                    st.write("**Income by Type:**")
                    for income_type, amount in income_analysis['income_by_type'].items():
                        st.write(f"• {income_type}: {format_currency(amount)}")

            with col2:
                st.subheader("Daily Income")
                if not income_analysis['income_by_day'].empty:
                    daily_income_df = income_analysis['income_by_day'].reset_index()
                    daily_income_df['date'] = pd.to_datetime(daily_income_df['date'])

                    fig = px.line(
                        daily_income_df,
                        x='date',
                        y='income',
                        title='Daily Income',
                        labels={'income': 'Income (USDT)', 'date': 'Date'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Recent income table
            if not income_analysis['recent_income'].empty:
                st.subheader("Recent Income Records")
                recent_income_df = income_analysis['recent_income'].copy()

                # Format for display
                if 'time' in recent_income_df.columns:
                    recent_income_df['time'] = pd.to_datetime(recent_income_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')

                if 'income' in recent_income_df.columns:
                    recent_income_df['income'] = recent_income_df['income'].round(4)

                display_columns = ['time', 'symbol', 'incomeType', 'income', 'asset']
                available_columns = [col for col in display_columns if col in recent_income_df.columns]

                if available_columns:
                    display_data = recent_income_df[available_columns].copy()
                    display_data.columns = [col.replace('incomeType', 'Type').replace('income', 'Income').title() for col in display_data.columns]

                    st.dataframe(
                        display_data,
                        use_container_width=True,
                        hide_index=True,
                        height=300
                    )

    # Export functionality
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if not filtered_trades.empty and st.button("📥 Export Trades Data"):
            csv = filtered_trades.to_csv(index=False)
            st.download_button(
                label="Download Trades CSV",
                data=csv,
                file_name=f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col2:
        if not filtered_income.empty and st.button("📥 Export Income Data"):
            csv = filtered_income.to_csv(index=False)
            st.download_button(
                label="Download Income CSV",
                data=csv,
                file_name=f"income_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def create_trade_volume_chart(trades_df: pd.DataFrame):
    """Create trade volume chart over time"""
    if trades_df.empty:
        return go.Figure()

    # Group by date
    trades_df['date'] = pd.to_datetime(trades_df['time']).dt.date
    daily_volume = trades_df.groupby('date')['quoteQty'].sum().reset_index()
    daily_volume['date'] = pd.to_datetime(daily_volume['date'])

    fig = px.line(
        daily_volume,
        x='date',
        y='quoteQty',
        title='Daily Trading Volume',
        labels={'quoteQty': 'Volume (USDT)', 'date': 'Date'}
    )

    return fig

def create_symbol_performance_chart(trades_df: pd.DataFrame):
    """Create symbol performance chart"""
    if trades_df.empty:
        return go.Figure()

    # Group by symbol
    symbol_stats = trades_df.groupby('symbol').agg({
        'quoteQty': 'sum',
        'commission': 'sum',
        'realized_pnl': 'sum'
    }).reset_index()

    # Sort by volume
    symbol_stats = symbol_stats.nlargest(15, 'quoteQty')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Volume',
        x=symbol_stats['symbol'],
        y=symbol_stats['quoteQty'],
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        name='P&L',
        x=symbol_stats['symbol'],
        y=symbol_stats['realized_pnl'],
        marker_color=['green' if pnl >= 0 else 'red' for pnl in symbol_stats['realized_pnl']]
    ))

    fig.update_layout(
        title='Symbol Performance',
        xaxis_title='Symbol',
        yaxis_title='USDT',
        barmode='group'
    )

    return fig