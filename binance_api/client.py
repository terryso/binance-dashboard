import time
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from binance.client import Client as BinanceApiClient
from binance.exceptions import BinanceAPIException, BinanceRequestException
from config.secrets import SecretsManager

class BinanceClient:
    """Binance Futures API client wrapper"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.use_testnet = config.get('binance', {}).get('use_testnet', False)
        self.timeout = config.get('binance', {}).get('timeout', 30)
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Binance API client"""
        try:
            # Try to get credentials from secure storage first
            api_key = SecretsManager.get_api_key()
            secret_key = SecretsManager.get_secret_key()

            # Fallback to config (for temporary storage)
            if not api_key or not secret_key:
                api_key = self.config.get('binance', {}).get('api_key', '')
                secret_key = self.config.get('binance', {}).get('secret_key', '')

            if not api_key or not secret_key:
                raise ValueError("API credentials not found")

            # Initialize client
            self.client = BinanceApiClient(
                api_key=api_key,
                api_secret=secret_key,
                testnet=self.use_testnet
            )

        except Exception as e:
            raise Exception(f"Failed to initialize Binance client: {e}")

    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            if not self.client:
                return False
            server_time = self.client.ping()
            return server_time is not None
        except Exception:
            return False

    def get_account_info(self) -> Dict[str, Any]:
        """Get futures account information"""
        try:
            if not self.client:
                raise Exception("Client not initialized")

            account = self.client.futures_account()

            # Calculate total balance
            total_balance = 0.0
            for asset in account.get('assets', []):
                if float(asset.get('walletBalance', 0)) > 0:
                    total_balance += float(asset.get('walletBalance', 0))

            return {
                'total_balance': total_balance,
                'total_unrealized_pnl': float(account.get('totalUnrealizedPnl', 0)),
                'total_wallet_balance': float(account.get('totalWalletBalance', 0)),
                'available_balance': float(account.get('availableBalance', 0)),
                'margin_balance': float(account.get('totalMarginBalance', 0)),
                'assets': account.get('assets', []),
                'positions': account.get('positions', []),
                'update_time': datetime.now(timezone.utc).isoformat()
            }

        except BinanceAPIException as e:
            raise Exception(f"Binance API error: {e.message}")
        except Exception as e:
            raise Exception(f"Failed to get account info: {e}")

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current futures positions"""
        try:
            if not self.client:
                raise Exception("Client not initialized")

            positions = self.client.futures_position_information()

            # Filter positions with non-zero size
            active_positions = []
            for pos in positions:
                size = float(pos.get('positionAmt', 0))
                if abs(size) > 0:  # Non-zero positions
                    active_positions.append({
                        'symbol': pos.get('symbol', ''),
                        'position_side': pos.get('positionSide', ''),
                        'size': size,
                        'entry_price': float(pos.get('entryPrice', 0)),
                        'mark_price': float(pos.get('markPrice', 0)),
                        'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                        'percentage': float(pos.get('percentage', 0)),
                        'leverage': float(pos.get('leverage', 1)),
                        'margin_type': pos.get('marginType', ''),
                        'notional': float(pos.get('notional', 0)),
                        'update_time': datetime.now(timezone.utc).isoformat()
                    })

            return active_positions

        except BinanceAPIException as e:
            raise Exception(f"Binance API error: {e.message}")
        except Exception as e:
            raise Exception(f"Failed to get positions: {e}")

    def get_transaction_history(self, symbol: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """Get transaction history"""
        try:
            if not self.client:
                raise Exception("Client not initialized")

            trades = self.client.futures_account_trades(symbol=symbol, limit=limit)

            if not trades:
                return pd.DataFrame()

            df = pd.DataFrame(trades)

            # Convert relevant columns to numeric
            numeric_columns = ['qty', 'quoteQty', 'price', 'commission']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert timestamp
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'], unit='ms')

            # Calculate profit/loss for closed positions
            df['realized_pnl'] = df.apply(self._calculate_realized_pnl, axis=1)

            return df

        except BinanceAPIException as e:
            raise Exception(f"Binance API error: {e.message}")
        except Exception as e:
            raise Exception(f"Failed to get transaction history: {e}")

    def get_income_history(self, symbol: Optional[str] = None, limit: int = 100) -> pd.DataFrame:
        """Get income history"""
        try:
            if not self.client:
                raise Exception("Client not initialized")

            income = self.client.futures_income_history(symbol=symbol, limit=limit)

            if not income:
                return pd.DataFrame()

            df = pd.DataFrame(income)

            # Convert timestamp
            if 'time' in df.columns:
                df['time'] = pd.to_datetime(df['time'], unit='ms')

            # Convert numeric columns
            numeric_columns = ['income']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except BinanceAPIException as e:
            raise Exception(f"Binance API error: {e.message}")
        except Exception as e:
            raise Exception(f"Failed to get income history: {e}")

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information"""
        try:
            if not self.client:
                raise Exception("Client not initialized")

            exchange_info = self.client.futures_exchange_info()

            for sym_info in exchange_info.get('symbols', []):
                if sym_info.get('symbol') == symbol:
                    return sym_info

            raise Exception(f"Symbol {symbol} not found")

        except BinanceAPIException as e:
            raise Exception(f"Binance API error: {e.message}")
        except Exception as e:
            raise Exception(f"Failed to get symbol info: {e}")

    def _calculate_realized_pnl(self, row) -> float:
        """Calculate realized PnL for a trade"""
        # This is a simplified calculation
        # In a real implementation, you'd need to track position opening/closing
        side = row.get('side', '')
        qty = float(row.get('qty', 0))
        price = float(row.get('price', 0))
        commission = float(row.get('commission', 0))

        # This is a placeholder - proper PnL calculation requires tracking position state
        return -commission  # Return negative commission for now