from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

@dataclass
class Asset:
    """Represents an asset in the account"""
    symbol: str
    wallet_balance: float
    unrealized_pnl: float
    margin_balance: float
    maint_margin: float
    initial_margin: float
    position_initial_margin: float
    open_order_initial_margin: float
    cross_wallet_balance: float
    cross_unpnl: float
    available_balance: float
    max_withdraw_amount: float
    margin_available: bool
    update_time: datetime

    @classmethod
    def from_api_response(cls, asset_data: Dict[str, Any]) -> 'Asset':
        """Create Asset instance from API response"""
        return cls(
            symbol=asset_data.get('asset', ''),
            wallet_balance=float(asset_data.get('walletBalance', 0)),
            unrealized_pnl=float(asset_data.get('unrealizedPnl', 0)),
            margin_balance=float(asset_data.get('marginBalance', 0)),
            maint_margin=float(asset_data.get('maintMargin', 0)),
            initial_margin=float(asset_data.get('initialMargin', 0)),
            position_initial_margin=float(asset_data.get('positionInitialMargin', 0)),
            open_order_initial_margin=float(asset_data.get('openOrderInitialMargin', 0)),
            cross_wallet_balance=float(asset_data.get('crossWalletBalance', 0)),
            cross_unpnl=float(asset_data.get('crossUnPnl', 0)),
            available_balance=float(asset_data.get('availableBalance', 0)),
            max_withdraw_amount=float(asset_data.get('maxWithdrawAmount', 0)),
            margin_available=asset_data.get('marginAvailable', False),
            update_time=datetime.now()
        )

@dataclass
class Position:
    """Represents a futures position"""
    symbol: str
    position_side: str
    size: float
    entry_price: float
    mark_price: float
    unrealized_pnl: float
    percentage: float
    leverage: float
    margin_type: str
    notional: float
    update_time: datetime

    @classmethod
    def from_api_response(cls, position_data: Dict[str, Any]) -> 'Position':
        """Create Position instance from API response"""
        return cls(
            symbol=position_data.get('symbol', ''),
            position_side=position_data.get('positionSide', ''),
            size=float(position_data.get('size', 0)),
            entry_price=float(position_data.get('entryPrice', 0)),
            mark_price=float(position_data.get('markPrice', 0)),
            unrealized_pnl=float(position_data.get('unrealized_pnl', 0)),
            percentage=float(position_data.get('percentage', 0)),
            leverage=float(position_data.get('leverage', 1)),
            margin_type=position_data.get('margin_type', ''),
            notional=float(position_data.get('notional', 0)),
            update_time=datetime.now()
        )

    @property
    def is_long(self) -> bool:
        """Check if position is long"""
        return self.size > 0

    @property
    def is_short(self) -> bool:
        """Check if position is short"""
        return self.size < 0

    @property
    def pnl_percentage(self) -> float:
        """Calculate PnL percentage"""
        if self.entry_price == 0:
            return 0.0
        return (self.mark_price - self.entry_price) / self.entry_price * 100 * (1 if self.is_long else -1)

@dataclass
class Trade:
    """Represents a trade transaction"""
    symbol: str
    side: str
    quantity: float
    price: float
    commission: float
    commission_asset: str
    time: datetime
    order_id: int
    order_list_id: int
    real_pnl: float = 0.0

    @classmethod
    def from_api_response(cls, trade_data: Dict[str, Any]) -> 'Trade':
        """Create Trade instance from API response"""
        return cls(
            symbol=trade_data.get('symbol', ''),
            side=trade_data.get('side', ''),
            quantity=float(trade_data.get('qty', 0)),
            price=float(trade_data.get('price', 0)),
            commission=float(trade_data.get('commission', 0)),
            commission_asset=trade_data.get('commissionAsset', ''),
            time=datetime.fromtimestamp(int(trade_data.get('time', 0)) / 1000),
            order_id=int(trade_data.get('orderId', 0)),
            order_list_id=int(trade_data.get('orderListId', -1))
        )

@dataclass
class IncomeRecord:
    """Represents an income record"""
    symbol: str
    income_type: str
    income: float
    asset: str
    time: datetime
    transaction_id: int
    trade_id: int

    @classmethod
    def from_api_response(cls, income_data: Dict[str, Any]) -> 'IncomeRecord':
        """Create IncomeRecord instance from API response"""
        return cls(
            symbol=income_data.get('symbol', ''),
            income_type=income_data.get('incomeType', ''),
            income=float(income_data.get('income', 0)),
            asset=income_data.get('asset', ''),
            time=datetime.fromtimestamp(int(income_data.get('time', 0)) / 1000),
            transaction_id=int(income_data.get('tranId', 0)),
            trade_id=int(income_data.get('tradeId', 0))
        )

@dataclass
class AccountSummary:
    """Represents account summary information"""
    total_balance: float
    total_unrealized_pnl: float
    total_wallet_balance: float
    available_balance: float
    margin_balance: float
    assets: List[Asset]
    positions: List[Position]
    update_time: datetime

    @classmethod
    def from_api_response(cls, account_data: Dict[str, Any]) -> 'AccountSummary':
        """Create AccountSummary instance from API response"""
        assets = [Asset.from_api_response(asset) for asset in account_data.get('assets', [])]
        positions = [Position.from_api_response(pos) for pos in account_data.get('positions', []) if abs(float(pos.get('positionAmt', 0))) > 0]

        return cls(
            total_balance=float(account_data.get('total_balance', 0)),
            total_unrealized_pnl=float(account_data.get('total_unrealized_pnl', 0)),
            total_wallet_balance=float(account_data.get('total_wallet_balance', 0)),
            available_balance=float(account_data.get('available_balance', 0)),
            margin_balance=float(account_data.get('margin_balance', 0)),
            assets=assets,
            positions=positions,
            update_time=datetime.now()
        )

    @property
    def total_pnl(self) -> float:
        """Calculate total PnL including realized and unrealized"""
        return self.total_unrealized_pnl

    @property
    def active_positions_count(self) -> int:
        """Get count of active positions"""
        return len(self.positions)

    @property
    def total_notional_value(self) -> float:
        """Calculate total notional value of all positions"""
        return sum(pos.notional for pos in self.positions)