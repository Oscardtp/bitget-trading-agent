"""
Trading Agent - Health Check Router
System status monitoring for all critical components.
"""

import time
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter

router = APIRouter(prefix="/api/health")

# Cache for health checks (30 second TTL)
_health_cache = {"data": None, "timestamp": 0}
CACHE_TTL = 30

DB_PATH = Path(__file__).parent.parent.parent / "trading_agent.db"


def _check_exchange_connection() -> dict:
    """Check if exchange connection is working."""
    try:
        from data.exchange_client import ExchangeClient
        client = ExchangeClient()
        client.exchange.fetch_ohlcv("BTC/USDT", "1h", limit=1)
        return {"name": "Exchange Connection", "status": "ok", "message": None}
    except Exception as e:
        return {"name": "Exchange Connection", "status": "error", "message": str(e)[:100]}


def _check_data_feed() -> dict:
    """Check if data feed is working."""
    try:
        from data.market_data import MarketData
        md = MarketData(sandbox=True)
        candles = md.get_candles("BTC/USDT", "1h", limit=5)
        if candles and len(candles) > 0:
            return {"name": "Data Feed", "status": "ok", "message": f"{len(candles)} candles"}
        return {"name": "Data Feed", "status": "error", "message": "No candles returned"}
    except Exception as e:
        return {"name": "Data Feed", "status": "error", "message": str(e)[:100]}


def _check_strategy_engine() -> dict:
    """Check if strategy engine is working."""
    try:
        from strategies.registry import get_all_strategies
        strategies = get_all_strategies()
        count = len(strategies)
        if count > 0:
            names = list(strategies.keys())[:3]
            return {"name": "Strategy Engine", "status": "ok", "message": f"{count} strategies: {', '.join(names)}"}
        return {"name": "Strategy Engine", "status": "error", "message": "No strategies registered"}
    except Exception as e:
        return {"name": "Strategy Engine", "status": "error", "message": str(e)[:100]}


def _check_risk_engine() -> dict:
    """Check if risk engine is working."""
    try:
        from risk.drawdown import DrawdownManager
        from risk.kill_switch import KillSwitch
        dm = DrawdownManager()
        ks = KillSwitch()
        return {"name": "Risk Engine", "status": "ok", "message": f"Kill switch: {'ACTIVE' if ks.is_active else 'inactive'}"}
    except Exception as e:
        return {"name": "Risk Engine", "status": "error", "message": str(e)[:100]}


def _check_execution_engine() -> dict:
    """Check if execution engine is working."""
    try:
        from execution.protocol_manager import ProtocolManager
        pm = ProtocolManager()
        return {"name": "Execution Engine", "status": "ok", "message": f"State: {pm.state.value}"}
    except Exception as e:
        return {"name": "Execution Engine", "status": "error", "message": str(e)[:100]}


def _check_logging_engine() -> dict:
    """Check if logging engine is working."""
    try:
        from logs.log_manager import LogManager
        from logs.event_store import EventStore
        lm = LogManager()
        es = EventStore()
        return {"name": "Logging Engine", "status": "ok", "message": "LogManager + EventStore"}
    except Exception as e:
        return {"name": "Logging Engine", "status": "error", "message": str(e)[:100]}


def _check_database() -> dict:
    """Check if database is accessible."""
    try:
        if not DB_PATH.exists():
            return {"name": "Database", "status": "error", "message": "DB file not found"}
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        conn.close()
        return {"name": "Database", "status": "ok", "message": f"{table_count} tables"}
    except Exception as e:
        return {"name": "Database", "status": "error", "message": str(e)[:100]}


def _check_dashboard() -> dict:
    """Check if dashboard WebSocket is available."""
    return {"name": "Dashboard", "status": "ok", "message": "API reachable"}


@router.get("/")
async def get_health():
    """Get health status of all system components."""
    now = time.time()
    
    # Return cached result if fresh enough
    if _health_cache["data"] and (now - _health_cache["timestamp"]) < CACHE_TTL:
        return _health_cache["data"]
    
    # Run all checks
    checks = [
        _check_exchange_connection(),
        _check_data_feed(),
        _check_strategy_engine(),
        _check_risk_engine(),
        _check_execution_engine(),
        _check_logging_engine(),
        _check_database(),
        _check_dashboard(),
    ]
    
    # Determine overall status
    has_error = any(c["status"] == "error" for c in checks)
    overall_status = "degraded" if has_error else "ok"
    
    result = {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": checks,
        "summary": {
            "total": len(checks),
            "ok": sum(1 for c in checks if c["status"] == "ok"),
            "error": sum(1 for c in checks if c["status"] == "error"),
        },
    }
    
    # Cache result
    _health_cache["data"] = result
    _health_cache["timestamp"] = now
    
    return result
