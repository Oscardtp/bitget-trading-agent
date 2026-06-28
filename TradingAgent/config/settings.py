"""
Trading Agent - Configuration Settings
All settings use Pydantic for validation and type safety.
"""

from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class RiskSettings(BaseModel):
    """Risk management parameters."""
    base: float = Field(default=0.01, description="Base risk per trade (1%)")
    min: float = Field(default=0.005, description="Minimum risk per trade (0.5%)")
    max: float = Field(default=0.05, description="Maximum risk per trade (5%)")
    rr_min: float = Field(default=2.0, description="Minimum risk-reward ratio")
    max_positions: int = Field(default=3, description="Maximum simultaneous positions")
    max_trades_day: int = Field(default=5, description="Maximum trades per day")
    max_drawdown_daily: float = Field(default=0.05, description="Maximum daily drawdown (5%)")
    max_consecutive_losses: int = Field(default=3, description="Max consecutive losses before reduction")
    max_slippage: float = Field(default=0.005, description="Maximum allowed slippage (0.5%)")


class StrategySettings(BaseModel):
    """Strategy selection parameters."""
    threshold: float = Field(default=0.65, description="Minimum strategy score to activate")
    confidence_threshold: float = Field(default=0.65, description="Minimum confidence for trade")
    duration_limits: dict = Field(
        default={
            "scalping": 6,
            "swing": 360,
            "breakout": 72,
            "mean_reversion": 12,
        },
        description="Duration limits in hours per strategy type"
    )


class TimingSettings(BaseModel):
    """Timing and interval parameters."""
    scanner_interval: int = Field(default=300, description="Scanner interval in seconds (5 min)")
    monitor_interval: int = Field(default=120, description="Monitor interval in seconds (2 min)")


class BitgetSettings(BaseModel):
    """Bitget exchange API settings."""
    api_key: str = Field(default="", description="Bitget API key")
    secret: str = Field(default="", description="Bitget API secret")
    passphrase: str = Field(default="", description="Bitget API passphrase")
    sandbox: bool = Field(default=True, description="Use sandbox mode")
    base_url: str = Field(default="https://api.bitget.com", description="Bitget API base URL")


class DatabaseSettings(BaseModel):
    """Database configuration."""
    url: str = Field(default="sqlite:///trading_agent.db", description="Database URL")
    echo: bool = Field(default=False, description="Enable SQL logging")


class Settings(BaseSettings):
    """Main application settings."""
    # Risk
    risk: RiskSettings = Field(default_factory=RiskSettings)
    
    # Strategy
    strategy: StrategySettings = Field(default_factory=StrategySettings)
    
    # Timing
    timing: TimingSettings = Field(default_factory=TimingSettings)
    
    # Exchange
    bitget: BitgetSettings = Field(default_factory=BitgetSettings)
    
    # Database
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    
    # General
    asset: str = Field(default="BTCUSDT", description="Default trading asset")
    log_level: str = Field(default="INFO", description="Logging level")
    
    model_config = {
        "env_prefix": "TA_",
        "env_nested_delimiter": "__",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
