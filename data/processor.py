import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from binance_api.models import Trade, Position, AccountSummary, Asset
from binance_api.utils import safe_float, format_currency, format_percentage

class DataProcessor:
    """Processes and analyzes trading data"""

    def __init__(self):
        self.cache_timeout = 60  # seconds

    def process_account_summary(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process account summary data for display"""
        summary = AccountSummary.from_api_response(account_data)

        # Calculate additional metrics
        total_investment = sum(asset.wallet_balance for asset in summary.assets if asset.symbol != 'USDT')
        usdt_balance = next((asset.wallet_balance for asset in summary.assets if asset.symbol == 'USDT'), 0)

        # Calculate portfolio metrics
        active_positions_value = sum(abs(pos.notional) for pos in summary.positions)
        total_exposure = active_positions_value
        leverage_usage = (total_exposure / summary.total_balance) if summary.total_balance > 0 else 0

        return {
            'total_balance': summary.total_balance,
            'available_balance': summary.available_balance,
            'total_pnl': summary.total_unrealized_pnl,
            'pnl_percentage': (summary.total_unrealized_pnl / (summary.total_balance - summary.total_unrealized_pnl) * 100) if summary.total_balance > 0 else 0,
            'margin_balance': summary.margin_balance,
            'active_positions': summary.active_positions_count,
            'total_exposure': total_exposure,
            'leverage_usage': leverage_usage,
            'usdt_balance': usdt_balance,
            'other_assets_balance': total_investment,
            'update_time': summary.update_time,
            'assets': self._process_assets(summary.assets),
            'positions_summary': self._summarize_positions(summary.positions)
        }

    def _process_assets(self, assets: List[Asset]) -> List[Dict[str, Any]]:
        """Process asset list for display"""
        processed_assets = []
        for asset in assets:
            if asset.wallet_balance > 0:  # Only show assets with balance
                processed_assets.append({
                    'symbol': asset.symbol,
                    'balance': asset.wallet_balance,
                    'formatted_balance': format_currency(asset.wallet_balance, asset.symbol),
                    'unrealized_pnl': asset.unrealized_pnl,
                    'formatted_pnl': format_currency(asset.unrealized_pnl),
                    'available_balance': asset.available_balance,
                    'margin_balance': asset.margin_balance
                })
        return processed_assets

    def _summarize_positions(self, positions: List[Position]) -> Dict[str, Any]:
        """Create summary of positions"""
        if not positions:
            return {
                'total_notional': 0,
                'total_unrealized_pnl': 0,
                'long_positions': 0,
                'short_positions': 0,
                'avg_leverage': 1.0
            }

        total_notional = sum(abs(pos.notional) for pos in positions)
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        long_positions = sum(1 for pos in positions if pos.is_long)
        short_positions = sum(1 for pos in positions if pos.is_short)
        avg_leverage = sum(pos.leverage for pos in positions) / len(positions)

        return {
            'total_notional': total_notional,
            'total_unrealized_pnl': total_unrealized_pnl,
            'long_positions': long_positions,
            'short_positions': short_positions,
            'avg_leverage': avg_leverage
        }

    def process_trades_data(self, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """Process trades data for analysis"""
        if trades_df.empty:
            return {
                'total_trades': 0,
                'total_volume': 0,
                'total_commission': 0,
                'win_rate': 0,
                'avg_trade_size': 0,
                'trades_by_symbol': {},
                'trades_by_day': pd.DataFrame()
            }

        # Ensure data types
        numeric_columns = ['qty', 'quoteQty', 'price', 'commission', 'realized_pnl']
        for col in numeric_columns:
            if col in trades_df.columns:
                trades_df[col] = pd.to_numeric(trades_df[col], errors='coerce')

        # Basic statistics
        total_trades = len(trades_df)
        total_volume = trades_df['quoteQty'].sum() if 'quoteQty' in trades_df.columns else 0
        total_commission = trades_df['commission'].sum() if 'commission' in trades_df.columns else 0

        # Trade analysis
        avg_trade_size = trades_df['qty'].mean() if 'qty' in trades_df.columns else 0

        # Group by symbol
        trades_by_symbol = {}
        if 'symbol' in trades_df.columns:
            symbol_stats = trades_df.groupby('symbol').agg({
                'qty': 'count',
                'quoteQty': 'sum',
                'commission': 'sum'
            }).rename(columns={'qty': 'trade_count'})
            trades_by_symbol = symbol_stats.to_dict('index')

        # Group by day
        trades_by_day = pd.DataFrame()
        if 'time' in trades_df.columns:
            trades_df['date'] = pd.to_datetime(trades_df['time']).dt.date
            daily_stats = trades_df.groupby('date').agg({
                'qty': 'count',
                'quoteQty': 'sum',
                'commission': 'sum'
            }).rename(columns={'qty': 'trade_count'})
            trades_by_day = daily_stats

        return {
            'total_trades': total_trades,
            'total_volume': total_volume,
            'total_commission': total_commission,
            'avg_trade_size': avg_trade_size,
            'trades_by_symbol': trades_by_symbol,
            'trades_by_day': trades_by_day
        }

    def process_positions_data(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process positions data for display"""
        processed_positions = []

        for pos in positions:
            # Calculate metrics
            size = safe_float(pos.get('size', 0))
            entry_price = safe_float(pos.get('entry_price', 0))
            mark_price = safe_float(pos.get('mark_price', 0))
            unrealized_pnl = safe_float(pos.get('unrealized_pnl', 0))
            leverage = safe_float(pos.get('leverage', 1))
            notional = safe_float(pos.get('notional', 0))

            # Calculate PnL percentage
            pnl_percentage = 0
            if entry_price > 0:
                pnl_percentage = ((mark_price - entry_price) / entry_price * 100) * (1 if size > 0 else -1)

            processed_position = {
                'symbol': pos.get('symbol', ''),
                'formatted_symbol': self._format_symbol(pos.get('symbol', '')),
                'side': 'LONG' if size > 0 else 'SHORT',
                'size': abs(size),
                'formatted_size': f"{abs(size):.4f}",
                'entry_price': entry_price,
                'formatted_entry_price': f"{entry_price:.4f}",
                'mark_price': mark_price,
                'formatted_mark_price': f"{mark_price:.4f}",
                'unrealized_pnl': unrealized_pnl,
                'formatted_pnl': format_currency(unrealized_pnl),
                'pnl_percentage': pnl_percentage,
                'formatted_percentage': format_percentage(pnl_percentage),
                'leverage': leverage,
                'notional': abs(notional),
                'formatted_notional': format_currency(abs(notional)),
                'margin_type': pos.get('margin_type', 'cross'),
                'pnl_color': 'green' if unrealized_pnl > 0 else 'red' if unrealized_pnl < 0 else 'gray'
            }

            processed_positions.append(processed_position)

        # Sort by PnL (absolute value)
        processed_positions.sort(key=lambda x: abs(x['unrealized_pnl']), reverse=True)

        return processed_positions

    def process_income_data(self, income_df: pd.DataFrame) -> Dict[str, Any]:
        """Process income data for analysis"""
        if income_df.empty:
            return {
                'total_income': 0,
                'income_by_type': {},
                'income_by_day': pd.DataFrame(),
                'recent_income': pd.DataFrame()
            }

        # Ensure data types
        if 'income' in income_df.columns:
            income_df['income'] = pd.to_numeric(income_df['income'], errors='coerce')

        if 'time' in income_df.columns:
            income_df['time'] = pd.to_datetime(income_df['time'])

        # Total income
        total_income = income_df['income'].sum()

        # Group by income type
        income_by_type = {}
        if 'incomeType' in income_df.columns:
            type_stats = income_df.groupby('incomeType')['income'].sum()
            income_by_type = type_stats.to_dict()

        # Group by day
        income_by_day = pd.DataFrame()
        if 'time' in income_df.columns:
            income_df['date'] = income_df['time'].dt.date
            daily_income = income_df.groupby('date')['income'].sum()
            income_by_day = daily_income.to_frame('income')

        # Recent income
        recent_income = income_df.nlargest(10, 'time') if 'time' in income_df.columns else income_df.head(10)

        return {
            'total_income': total_income,
            'income_by_type': income_by_type,
            'income_by_day': income_by_day,
            'recent_income': recent_income
        }

    def calculate_performance_metrics(self, trades_df: pd.DataFrame, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        metrics = {
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'largest_win': 0,
            'largest_loss': 0
        }

        if trades_df.empty:
            return metrics

        # Calculate returns from trades
        if 'realized_pnl' in trades_df.columns:
            returns = trades_df['realized_pnl'].values
            returns = returns[returns != 0]  # Remove zero returns

            if len(returns) > 0:
                # Win rate
                winning_trades = returns[returns > 0]
                losing_trades = returns[returns < 0]

                metrics['win_rate'] = len(winning_trades) / len(returns) * 100 if len(returns) > 0 else 0
                metrics['avg_win'] = winning_trades.mean() if len(winning_trades) > 0 else 0
                metrics['avg_loss'] = losing_trades.mean() if len(losing_trades) > 0 else 0
                metrics['largest_win'] = winning_trades.max() if len(winning_trades) > 0 else 0
                metrics['largest_loss'] = losing_trades.min() if len(losing_trades) > 0 else 0

                # Profit factor
                total_wins = winning_trades.sum() if len(winning_trades) > 0 else 0
                total_losses = abs(losing_trades.sum()) if len(losing_trades) > 0 else 0
                metrics['profit_factor'] = total_wins / total_losses if total_losses > 0 else float('inf')

                # Sharpe ratio (simplified)
                if len(returns) > 1:
                    import numpy as np
                    returns_series = pd.Series(returns)
                    metrics['sharpe_ratio'] = (returns_series.mean() / returns_series.std()) * np.sqrt(365) if returns_series.std() > 0 else 0

        return metrics

    def _format_symbol(self, symbol: str) -> str:
        """Format trading symbol for display"""
        if '/' not in symbol and symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}/USDT"
        return symbol