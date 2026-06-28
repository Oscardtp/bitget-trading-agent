"""
Trading Agent - Main Entry Point
Hypothesis-based crypto trading agent for Bitget.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for the application."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("trading_agent.log", mode="a"),
        ],
    )
    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("ccxt").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Trading Agent - Hypothesis-based crypto trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run with default settings
  python main.py --dry-run          # Run without executing trades
  python main.py --log-level DEBUG  # Run with debug logging
  python main.py --init-db          # Initialize database only
        """,
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no real trades)",
    )
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database and exit",
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: INFO)",
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config file (default: .env)",
    )
    
    parser.add_argument(
        "--asset",
        type=str,
        default="BTCUSDT",
        help="Trading asset (default: BTCUSDT)",
    )
    
    return parser.parse_args()


def init_database() -> bool:
    """Initialize the database. Returns True on success."""
    try:
        from db.database import init_db
        init_db()
        return True
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        return False


def main() -> int:
    """Main entry point."""
    args = parse_args()
    setup_logging(args.log_level)
    
    logger = logging.getLogger("main")
    logger.info("=" * 60)
    logger.info("Trading Agent - Starting")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"Asset: {args.asset}")
    logger.info(f"Log level: {args.log_level}")
    logger.info("=" * 60)
    
    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database...")
        if init_database():
            logger.info("Database initialized successfully")
            return 0
        else:
            logger.error("Database initialization failed")
            return 1
    
    # Initialize database
    logger.info("Initializing database...")
    if not init_database():
        logger.error("Cannot continue without database")
        return 1
    
    # Load settings
    try:
        from config.settings import get_settings
        settings = get_settings()
        logger.info(f"Settings loaded - Risk: {settings.risk.base:.1%}, Threshold: {settings.strategy.threshold}")
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        return 1
    
    # Main loop placeholder
    logger.info("Main loop not yet implemented (Fase 12)")
    logger.info("Infrastructure setup complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
