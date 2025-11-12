import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from data.processor import DataProcessor
from data.cache import get_cached_api
from binance_api.utils import format_currency, format_percentage, get_leverage_risk_score, calculate_position_size_risk

def show_positions():
    """Display positions page"""
    st.title("🔍 Positions Management")
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

    # Load positions data
    with st.spinner("Loading positions data..."):
        try:
            positions = cached_api.cached_positions(client)
            processed_positions = processor.process_positions_data(positions)
        except Exception as e:
            st.error(f"❌ Error loading positions: {e}")
            return

    if not processed_positions:
        st.info("No active positions found")
        return

    # Filters sidebar
    st.sidebar.markdown("### 🔧 Filters")

    # Filter by side
    sides = ['All', 'LONG', 'SHORT']
    selected_side = st.sidebar.selectbox("Filter by Side", sides)

    # Filter by PnL
    pnl_filter = st.sidebar.selectbox("Filter by P&L", ['All', 'Profitable', 'Losing'])

    # Leverage filter
    leverage_threshold = st.sidebar.slider("Minimum Leverage", 1, 50, 1)

    # Apply filters
    filtered_positions = []
    for pos in processed_positions:
        # Side filter
        if selected_side != 'All' and pos['side'] != selected_side:
            continue

        # PnL filter
        if pnl_filter == 'Profitable' and pos['unrealized_pnl'] <= 0:
            continue
        elif pnl_filter == 'Losing' and pos['unrealized_pnl'] > 0:
            continue

        # Leverage filter
        if pos['leverage'] < leverage_threshold:
            continue

        filtered_positions.append(pos)

    # Summary metrics
    st.markdown("### 📊 Position Summary")
    col1, col2, col3, col4 = st.columns(4)

    total_notional = sum(pos['notional'] for pos in filtered_positions)
    total_pnl = sum(pos['unrealized_pnl'] for pos in filtered_positions)
    long_positions = sum(1 for pos in filtered_positions if pos['side'] == 'LONG')
    short_positions = sum(1 for pos in filtered_positions if pos['side'] == 'SHORT')
    avg_leverage = sum(pos['leverage'] for pos in filtered_positions) / len(filtered_positions) if filtered_positions else 0

    with col1:
        st.metric("Total Notional", format_currency(total_notional))
    with col2:
        st.metric("Total P&L", format_currency(total_pnl), format_percentage((total_pnl / (total_notional - total_pnl)) * 100 if total_notional > 0 else 0))
    with col3:
        st.metric("Long/Short", f"{long_positions}/{short_positions}")
    with col4:
        st.metric("Avg Leverage", f"{avg_leverage:.1f}x")

    st.markdown("---")

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 P&L Distribution")
        if filtered_positions:
            pnl_df = pd.DataFrame(filtered_positions)
            fig = px.bar(
                pnl_df,
                x='formatted_symbol',
                y='unrealized_pnl',
                color='unrealized_pnl',
                color_continuous_scale=['red', 'yellow', 'green'],
                title='P&L by Position'
            )
            fig.update_layout(showlegend=False, xaxis_title="Symbol", yaxis_title="P&L (USDT)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No positions match the filters")

    with col2:
        st.subheader("⚖️ Long vs Short Exposure")
        if filtered_positions:
            long_exposure = sum(pos['notional'] for pos in filtered_positions if pos['side'] == 'LONG')
            short_exposure = sum(pos['notional'] for pos in filtered_positions if pos['side'] == 'SHORT')

            fig = go.Figure(data=[
                go.Bar(name='Long', x=['Exposure'], y=[long_exposure], marker_color='green'),
                go.Bar(name='Short', x=['Exposure'], y=[short_exposure], marker_color='red')
            ])
            fig.update_layout(
                title='Long vs Short Exposure',
                yaxis_title='Notional Value (USDT)',
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No positions match the filters")

    st.markdown("---")

    # Risk Analysis
    st.subheader("⚠️ Risk Analysis")

    if filtered_positions:
        # Calculate risk metrics for each position
        risk_data = []
        for pos in filtered_positions:
            position_risk = calculate_position_size_risk(pos)
            leverage_risk = get_leverage_risk_score(pos['leverage'])

            risk_data.append({
                'Symbol': pos['symbol'],
                'Side': pos['side'],
                'Size Risk': position_risk['size_risk'],
                'Leverage Risk': leverage_risk['level'],
                'Total Risk Score': position_risk['total_risk_score']
            })

        risk_df = pd.DataFrame(risk_data)

        col1, col2 = st.columns(2)

        with col1:
            # Risk distribution
            risk_counts = risk_df['Total Risk Score'].value_counts().sort_index()
            fig = px.bar(
                x=risk_counts.index,
                y=risk_counts.values,
                title='Risk Score Distribution',
                labels={'x': 'Risk Score', 'y': 'Number of Positions'}
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Risk table
            st.dataframe(
                risk_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol"),
                    "Side": st.column_config.TextColumn("Side"),
                    "Size Risk": st.column_config.TextColumn("Size Risk"),
                    "Leverage Risk": st.column_config.TextColumn("Leverage Risk"),
                    "Total Risk Score": st.column_config.ProgressColumn(
                        "Total Risk",
                        help="Combined risk score from position size and leverage",
                        format="%.f",
                        min_value=0,
                        max_value=8
                    )
                }
            )

    st.markdown("---")

    # Detailed positions table
    st.subheader("📋 Detailed Positions")

    if filtered_positions:
        # Create dataframe for display
        positions_df = pd.DataFrame(filtered_positions)

        # Select columns for display
        display_columns = [
            'formatted_symbol',
            'side',
            'formatted_size',
            'formatted_entry_price',
            'formatted_mark_price',
            'formatted_pnl',
            'formatted_percentage',
            'leverage',
            'formatted_notional',
            'margin_type'
        ]

        if all(col in positions_df.columns for col in display_columns):
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
                'Notional',
                'Margin Type'
            ]

            # Add color based on P&L
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
                    "Notional": st.column_config.TextColumn("Notional"),
                    "Margin Type": st.column_config.TextColumn("Margin Type")
                }
            )
    else:
        st.info("No positions match the current filters")

    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Positions Data"):
        if filtered_positions:
            export_df = pd.DataFrame(filtered_positions)
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def create_leverage_chart(positions_data: list):
    """Create leverage distribution chart"""
    if not positions_data:
        return go.Figure()

    df = pd.DataFrame(positions_data)

    fig = go.Figure(data=[
        go.Bar(
            x=df['formatted_symbol'],
            y=df['leverage'],
            marker_color='orange',
            text=[f"{lev:.1f}x" for lev in df['leverage']],
            textposition='auto'
        )
    ])

    fig.update_layout(
        title="Leverage by Position",
        xaxis_title="Symbol",
        yaxis_title="Leverage (x)"
    )

    return fig

def create_exposure_chart(positions_data: list):
    """Create exposure distribution chart"""
    if not positions_data:
        return go.Figure()

    df = pd.DataFrame(positions_data)

    # Group by side
    long_df = df[df['side'] == 'LONG']
    short_df = df[df['side'] == 'SHORT']

    fig = go.Figure()

    if not long_df.empty:
        fig.add_trace(go.Bar(
            name='Long',
            x=long_df['formatted_symbol'],
            y=long_df['notional'],
            marker_color='green'
        ))

    if not short_df.empty:
        fig.add_trace(go.Bar(
            name='Short',
            x=short_df['formatted_symbol'],
            y=short_df['notional'],
            marker_color='red'
        ))

    fig.update_layout(
        title="Position Exposure by Side",
        xaxis_title="Symbol",
        yaxis_title="Notional Value (USDT)",
        barmode='group'
    )

    return fig