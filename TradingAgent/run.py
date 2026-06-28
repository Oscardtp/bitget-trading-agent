"""
Trading Agent - Unified Entry Point
Starts API server + Trading Bot in a single process.
"""

import sys
import threading
import logging
import time
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def kill_port_process(port: int) -> None:
    """Kill any process listening on the given port."""
    logger = logging.getLogger("port_cleanup")
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5,
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = int(parts[-1])
                logger.info("Killing PID %d on port %d...", pid, port)
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F"],
                    capture_output=True, timeout=5,
                )
                logger.info("Killed process %d.", pid)
                return
    except Exception as e:
        logger.warning("Port cleanup failed: %s", e)


def start_api_server():
    """Start FastAPI server in background thread."""
    import uvicorn
    from api.config import get_api_settings

    settings = get_api_settings()
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        log_level="warning",
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Trading Agent - Unified (API + Bot)")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--scanner-interval", type=int, default=60)
    parser.add_argument("--monitor-interval", type=int, default=30)
    parser.add_argument("--context-interval", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--api-port", type=int, default=8000)
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("main")

    logger.info("=" * 60)
    logger.info("TRADING AGENT - Unified (API + Bot)")
    logger.info("=" * 60)

    # Start API server in background thread
    logger.info("Starting API server on port %d...", args.api_port)
    kill_port_process(args.api_port)
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    time.sleep(2)  # Wait for API to start

    # Start trading bot
    from main_loop import TradingLoop

    dry_run = not args.live
    loop = TradingLoop(
        symbol=args.symbol,
        scanner_interval=args.scanner_interval,
        monitor_interval=args.monitor_interval,
        context_interval=args.context_interval,
        dry_run=dry_run,
    )

    logger.info("Starting trading bot...")
    loop.start()


if __name__ == "__main__":
    main()
