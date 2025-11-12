import os
import toml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

def load_config() -> Dict[str, Any]:
    """Load configuration from TOML file and environment variables"""

    # Default configuration
    default_config = {
        "app": {
            "name": "Binance Futures Dashboard",
            "refresh_interval": 60,
            "theme": "dark"
        },
        "binance": {
            "use_testnet": False,
            "timeout": 30
        },
        "display": {
            "default_currency": "USDT",
            "timezone": "UTC",
            "date_format": "%Y-%m-%d %H:%M:%S"
        }
    }

    # Try to load from config file
    config_path = Path("config.toml")
    if config_path.exists():
        try:
            file_config = toml.load(config_path)
            # Merge with defaults
            for section in default_config:
                if section in file_config:
                    default_config[section].update(file_config[section])
        except Exception as e:
            print(f"Warning: Could not load config.toml: {e}")

    # Override with environment variables
    env_overrides = {
        "binance": {
            "api_key": os.getenv("BINANCE_API_KEY", ""),
            "secret_key": os.getenv("BINANCE_SECRET_KEY", ""),
            "use_testnet": os.getenv("USE_TESTNET", "false").lower() == "true"
        },
        "app": {
            "refresh_interval": int(os.getenv("REFRESH_INTERVAL", default_config["app"]["refresh_interval"]))
        }
    }

    # Apply environment overrides
    for section, overrides in env_overrides.items():
        for key, value in overrides.items():
            if value or isinstance(value, bool):  # Allow False values
                default_config[section][key] = value

    return default_config

def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable with default value"""
    return os.getenv(key, default)

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to TOML file"""
    try:
        config_path = Path("config.toml")
        # Don't save sensitive information
        safe_config = config.copy()
        if "api_key" in safe_config.get("binance", {}):
            del safe_config["binance"]["api_key"]
        if "secret_key" in safe_config.get("binance", {}):
            del safe_config["binance"]["secret_key"]

        with open(config_path, "w") as f:
            toml.dump(safe_config, f)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False