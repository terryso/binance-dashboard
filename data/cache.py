import time
import hashlib
import pickle
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import streamlit as st

class CacheManager:
    """Manages data caching for the application"""

    def __init__(self, default_timeout: int = 60):
        self.default_timeout = default_timeout
        self.cache_key_prefix = "binance_dashboard_"

    def get_cache_key(self, key: str, *args) -> str:
        """Generate a unique cache key"""
        if args:
            # Create a hash of arguments to include in key
            args_str = str(sorted(args))
            args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            return f"{self.cache_key_prefix}{key}_{args_hash}"
        return f"{self.cache_key_prefix}{key}"

    def get(self, key: str, default: Any = None) -> Any:
        """Get cached value"""
        cache_key = self.get_cache_key(key)

        if cache_key in st.session_state:
            cached_item = st.session_state[cache_key]
            if isinstance(cached_item, dict) and 'data' in cached_item and 'timestamp' in cached_item:
                # Check if cache is still valid
                if time.time() - cached_item['timestamp'] < cached_item['timeout']:
                    return cached_item['data']
                else:
                    # Cache expired, remove it
                    del st.session_state[cache_key]

        return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set cached value with timeout"""
        if timeout is None:
            timeout = self.default_timeout

        cache_key = self.get_cache_key(key)
        st.session_state[cache_key] = {
            'data': value,
            'timestamp': time.time(),
            'timeout': timeout
        }

    def clear(self, key: Optional[str] = None) -> None:
        """Clear cache entry or all cache"""
        if key:
            cache_key = self.get_cache_key(key)
            if cache_key in st.session_state:
                del st.session_state[cache_key]
        else:
            # Clear all cache entries
            keys_to_remove = [k for k in st.session_state.keys() if k.startswith(self.cache_key_prefix)]
            for k in keys_to_remove:
                del st.session_state[k]

    def is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        cache_key = self.get_cache_key(key)

        if cache_key in st.session_state:
            cached_item = st.session_state[cache_key]
            if isinstance(cached_item, dict) and 'timestamp' in cached_item:
                return time.time() - cached_item['timestamp'] >= cached_item['timeout']

        return True

    def get_or_compute(self, key: str, compute_func, timeout: Optional[int] = None, *args, **kwargs):
        """Get cached value or compute if not exists/expired"""
        # Generate cache key with arguments
        if args:
            cache_key = self.get_cache_key(key, *args)
        else:
            cache_key = self.get_cache_key(key)

        # Try to get from cache
        if not self.is_expired(key):
            cached_value = self.get(key)
            if cached_value is not None:
                return cached_value

        # Compute value
        value = compute_func(*args, **kwargs)

        # Cache the result
        self.set(key, value, timeout)

        return value

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_keys = [k for k in st.session_state.keys() if k.startswith(self.cache_key_prefix)]

        total_entries = len(cache_keys)
        expired_entries = 0
        total_size = 0

        for key in cache_keys:
            if key in st.session_state:
                cached_item = st.session_state[key]
                if isinstance(cached_item, dict):
                    total_size += len(pickle.dumps(cached_item))
                    if 'timestamp' in cached_item:
                        if time.time() - cached_item['timestamp'] >= cached_item['timeout']:
                            expired_entries += 1

        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'valid_entries': total_entries - expired_entries,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }

class CachedAPI:
    """Wrapper for API calls with caching"""

    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager

    def cached_account_info(self, client, timeout: int = 30) -> Dict[str, Any]:
        """Cached account info"""
        return self.cache.get_or_compute(
            'account_info',
            lambda: client.get_account_info(),
            timeout
        )

    def cached_positions(self, client, timeout: int = 30) -> list:
        """Cached positions"""
        return self.cache.get_or_compute(
            'positions',
            lambda: client.get_positions(),
            timeout
        )

    def cached_transaction_history(self, client, symbol: Optional[str] = None, limit: int = 100, timeout: int = 60) -> Any:
        """Cached transaction history"""
        cache_key = 'transaction_history'
        if symbol:
            cache_key = f'transaction_history_{symbol}'

        return self.cache.get_or_compute(
            cache_key,
            lambda: client.get_transaction_history(symbol, limit),
            timeout,
            symbol,
            limit
        )

    def cached_income_history(self, client, symbol: Optional[str] = None, limit: int = 100, timeout: int = 300) -> Any:
        """Cached income history (longer timeout)"""
        cache_key = 'income_history'
        if symbol:
            cache_key = f'income_history_{symbol}'

        return self.cache.get_or_compute(
            cache_key,
            lambda: client.get_income_history(symbol, limit),
            timeout,
            symbol,
            limit
        )

    def invalidate_cache(self, cache_type: str = 'all') -> None:
        """Invalidate specific or all cache entries"""
        if cache_type == 'all':
            self.cache.clear()
        elif cache_type == 'account':
            self.cache.clear('account_info')
            self.cache.clear('positions')
        elif cache_type == 'history':
            self.cache.clear('transaction_history')
            self.cache.clear('income_history')
        else:
            self.cache.clear(cache_type)

# Global cache instance
_cache_manager = CacheManager()
_cached_api = CachedAPI(_cache_manager)

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    return _cache_manager

def get_cached_api() -> CachedAPI:
    """Get global cached API instance"""
    return _cached_api

# Streamlit cache decorators for heavy computations
@st.cache_data(ttl=300)  # 5 minutes
def cached_dataframe_operation(df, operation_name: str, *args, **kwargs):
    """Cache expensive DataFrame operations"""
    # This is a generic cached function for DataFrame operations
    # You can create specific ones as needed
    if operation_name == 'group_by_symbol':
        return df.groupby('symbol').agg({
            'qty': 'count',
            'quoteQty': 'sum',
            'commission': 'sum'
        }).rename(columns={'qty': 'trade_count'})
    elif operation_name == 'daily_stats':
        if 'time' in df.columns:
            df['date'] = pd.to_datetime(df['time']).dt.date
            return df.groupby('date').agg({
                'qty': 'count',
                'quoteQty': 'sum',
                'commission': 'sum'
            }).rename(columns={'qty': 'trade_count'})
    return df

@st.cache_data(ttl=60)  # 1 minute
def cached_calculate_metrics(positions_data: list) -> dict:
    """Cache performance metrics calculations"""
    if not positions_data:
        return {'total_notional': 0, 'total_pnl': 0, 'count': 0}

    total_notional = sum(abs(pos.get('notional', 0)) for pos in positions_data)
    total_pnl = sum(pos.get('unrealized_pnl', 0) for pos in positions_data)

    return {
        'total_notional': total_notional,
        'total_pnl': total_pnl,
        'count': len(positions_data),
        'avg_notional': total_notional / len(positions_data) if positions_data else 0
    }