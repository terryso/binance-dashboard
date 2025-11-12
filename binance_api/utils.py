import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz

def format_currency(amount: float, currency: str = "USDT", decimal_places: int = 2) -> str:
    """Format currency amount with proper formatting"""
    if amount == 0:
        return f"$0.00 {currency}"

    sign = "-" if amount < 0 else ""
    abs_amount = abs(amount)

    if abs_amount >= 1e9:
        formatted = f"{abs_amount/1e9:.{decimal_places}f}B"
    elif abs_amount >= 1e6:
        formatted = f"{abs_amount/1e6:.{decimal_places}f}M"
    elif abs_amount >= 1e3:
        formatted = f"{abs_amount/1e3:.{decimal_places}f}K"
    else:
        formatted = f"{abs_amount:.{decimal_places}f}"

    return f"{sign}${formatted} {currency}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage with color coding"""
    if value == 0:
        return "0.00%"

    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimal_places}f}%"

def get_pnl_color(pnl: float) -> str:
    """Get color based on PnL value"""
    if pnl > 0:
        return "green"
    elif pnl < 0:
        return "red"
    else:
        return "gray"

def format_symbol(symbol: str) -> str:
    """Format trading symbol for display"""
    if '/' not in symbol:
        # Try to insert slash before USDT
        if symbol.endswith('USDT'):
            base = symbol[:-4]
            return f"{base}/USDT"
    return symbol

def calculate_time_ago(timestamp: datetime) -> str:
    """Calculate time ago from timestamp"""
    now = datetime.now(pytz.UTC)
    if timestamp.tzinfo is None:
        timestamp = pytz.UTC.localize(timestamp)

    diff = now - timestamp

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def round_to_precision(value: float, precision: int) -> float:
    """Round value to specified precision"""
    return round(value, precision)

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        if value is None or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        if value is None or value == '':
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def filter_dataframe(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply filters to DataFrame"""
    filtered_df = df.copy()

    for column, filter_value in filters.items():
        if column in filtered_df.columns:
            if isinstance(filter_value, (list, tuple)):
                # Filter for multiple values
                filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
            elif isinstance(filter_value, dict):
                # Apply range filter
                if 'min' in filter_value:
                    filtered_df = filtered_df[filtered_df[column] >= filter_value['min']]
                if 'max' in filter_value:
                    filtered_df = filtered_df[filtered_df[column] <= filter_value['max']]
            else:
                # Exact match
                filtered_df = filtered_df[filtered_df[column] == filter_value]

    return filtered_df

def get_date_range_preset(days: int) -> tuple[datetime, datetime]:
    """Get date range for preset number of days"""
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def validate_symbol(symbol: str) -> bool:
    """Validate trading symbol format"""
    if not symbol:
        return False

    # Basic validation - should contain letters and possibly end with USDT
    return len(symbol) >= 4 and symbol.replace('_', '').replace('-', '').isalnum()

def get_leverage_risk_score(leverage: float) -> Dict[str, Any]:
    """Get risk assessment based on leverage"""
    if leverage <= 2:
        risk_level = "Low"
        risk_color = "green"
        risk_score = 1
    elif leverage <= 5:
        risk_level = "Medium"
        risk_color = "orange"
        risk_score = 2
    elif leverage <= 10:
        risk_level = "High"
        risk_color = "red"
        risk_score = 3
    else:
        risk_level = "Very High"
        risk_color = "darkred"
        risk_score = 4

    return {
        "level": risk_level,
        "color": risk_color,
        "score": risk_score,
        "leverage": leverage
    }

def calculate_position_size_risk(position: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate risk metrics for a position"""
    size = abs(position.get('size', 0))
    notional = abs(position.get('notional', 0))
    leverage = position.get('leverage', 1)

    # Risk based on position size relative to typical portfolio
    if notional >= 10000:
        size_risk = "High"
        size_score = 3
    elif notional >= 5000:
        size_risk = "Medium"
        size_score = 2
    else:
        size_risk = "Low"
        size_score = 1

    return {
        "size_risk": size_risk,
        "size_score": size_score,
        "leverage_risk": get_leverage_risk_score(leverage),
        "total_risk_score": size_score + get_leverage_risk_score(leverage)["score"]
    }