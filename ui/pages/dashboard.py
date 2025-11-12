import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any

from data.processor import DataProcessor
from data.cache import get_cached_api
from binance_api.utils import format_currency, format_percentage, get_pnl_color

def show_dashboard():
    """Display main dashboard page"""
    st.title("📊 Binance Futures Dashboard")
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

    # Load data with caching
    with st.spinner("Loading account data..."):
        try:
            account_data = cached_api.cached_account_info(client)
            positions = cached_api.cached_positions(client)
            processed_data = processor.process_account_summary(account_data)
            processed_positions = processor.process_positions_data(positions)
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return

    # Dashboard layout
    col1, col2, col3, col4 = st.columns(4)

    # Key metrics
    with col1:
        st.metric(
            label="💰 Total Balance",
            value=format_currency(processed_data['total_balance']),
            delta=format_currency(processed_data['total_pnl'])
        )

    with col2:
        st.metric(
            label="📈 Available Balance",
            value=format_currency(processed_data['available_balance']),
            delta=f"{processed_data['active_positions']} positions"
        )

    with col3:
        st.metric(
            label="⚡ Leverage Usage",
            value=f"{processed_data['leverage_usage']:.1%}",
            delta=None
        )

    with col4:
        st.metric(
            label="📊 PnL",
            value=format_currency(processed_data['total_pnl']),
            delta=format_percentage(processed_data['pnl_percentage']),
            delta_color="normal" if processed_data['total_pnl'] >= 0 else "inverse"
        )

    st.markdown("---")

    # Charts and detailed sections
    col1, col2 = st.columns(2)

    with col1:
        # Asset distribution
        st.subheader("💎 Asset Distribution")
        if processed_data['assets']:
            asset_df = pd.DataFrame(processed_data['assets'])
            fig = px.pie(
                asset_df,
                values='balance',
                names='symbol',
                title='Asset Allocation'
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No assets to display")

    with col2:
        # PnL by position
        st.subheader("📈 Position P&L")
        if processed_positions:
            pnl_data = [(pos['formatted_symbol'], pos['unrealized_pnl'], pos['pnl_color']) for pos in processed_positions]
            pnl_df = pd.DataFrame(pnl_data, columns=['Symbol', 'PnL', 'Color'])

            fig = px.bar(
                pnl_df,
                x='Symbol',
                y='PnL',
                title='Unrealized P&L by Position',
                color='PnL',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No positions to display")

    st.markdown("---")

    # Active positions table
    st.subheader("🔍 Active Positions")
    if processed_positions:
        # Create dataframe for positions
        positions_df = pd.DataFrame(processed_positions)

        # Format for display
        display_columns = [
            'formatted_symbol',
            'side',
            'formatted_size',
            'formatted_entry_price',
            'formatted_mark_price',
            'formatted_pnl',
            'formatted_percentage',
            'leverage',
            'formatted_notional'
        ]

        if display_columns[0] in positions_df.columns:
            display_df = positions_df[display_columns].copy()
            display_df.columns = [
                'Symbol',
                'Side',
                'Size',
                'Entry Price',
                'Mark Price',
                'P&L',
                'P&L %',
                'Leverage',
                'Notional'
            ]

            # Add color formatting for P&L
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol"),
                    "Side": st.column_config.TextColumn("Side"),
                    "Size": st.column_config.TextColumn("Size"),
                    "Entry Price": st.column_config.TextColumn("Entry Price"),
                    "Mark Price": st.column_config.TextColumn("Mark Price"),
                    "P&L": st.column_config.TextColumn("P&L"),
                    "P&L %": st.column_config.TextColumn("P&L %"),
                    "Leverage": st.column_config.TextColumn("Leverage"),
                    "Notional": st.column_config.TextColumn("Notional")
                }
            )
    else:
        st.info("No active positions")

    st.markdown("---")

    # Performance overview
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Portfolio Overview")
        overview_data = {
            'Metric': ['Total Balance', 'Available', 'Total Exposure', 'Active Positions'],
            'Value': [
                format_currency(processed_data['total_balance']),
                format_currency(processed_data['available_balance']),
                format_currency(processed_data['total_exposure']),
                str(processed_data['active_positions'])
            ]
        }
        overview_df = pd.DataFrame(overview_data)
        st.dataframe(overview_df, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("⚠️ Risk Metrics")
        risk_data = {
            'Risk Metric': ['Leverage Usage', 'Position Count', 'Total P&L', 'Margin Balance'],
            'Value': [
                f"{processed_data['leverage_usage']:.1%}",
                str(processed_data['active_positions']),
                format_currency(processed_data['total_pnl']),
                format_currency(processed_data['margin_balance'])
            ]
        }
        risk_df = pd.DataFrame(risk_data)
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        cached_api.invalidate_cache('all')
        st.rerun()

    # Last update time
    st.caption(f"Last updated: {processed_data['update_time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")

def create_pnl_chart(positions_data: list):
    """Create PnL distribution chart"""
    if not positions_data:
        return go.Figure()

    df = pd.DataFrame(positions_data)

    fig = go.Figure(data=[
        go.Bar(
            x=df['formatted_symbol'],
            y=df['unrealized_pnl'],
            marker_color=['green' if pnl >= 0 else 'red' for pnl in df['unrealized_pnl']],
            text=df['formatted_pnl'],
            textposition='auto'
        )
    ])

    fig.update_layout(
        title="Unrealized P&L by Position",
        xaxis_title="Symbol",
        yaxis_title="P&L (USDT)",
        showlegend=False
    )

    return fig

def create_portfolio_pie_chart(assets_data: list):
    """Create portfolio distribution pie chart"""
    if not assets_data:
        return go.Figure()

    df = pd.DataFrame(assets_data)

    fig = go.Figure(data=[
        go.Pie(
            labels=df['symbol'],
            values=df['balance'],
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Balance: %{value}<br>Percentage: %{percent}'
        )
    ])

    fig.update_layout(title="Asset Distribution")

    return fig