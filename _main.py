"""
Main entry point for the cryptocurrency arbitrage trading system.

This module orchestrates the initialization and execution of the arbitrage engine,
handling configuration, logging, and graceful shutdown.
"""

import logging
import signal
import sys
from typing import NoReturn

from connectors.sushiswap import SushiSwapConnector
from connectors.uniswap import UniSwapConnector
from config.settings import load_settings
from core.arbitrage_engine import ArbitrageEngine
from core.price_aggregator import PriceAggregator
from utils.helpers import setup_logging
from utils.notifier import Notifier


logger = logging.getLogger(__name__)


class GracefulShutdown(Exception):
    """Exception raised to trigger graceful shutdown."""
    pass


def signal_handler(signum: int, frame) -> None:
    """
    Handle termination signals gracefully.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
    raise GracefulShutdown()


def initialize_engine() -> ArbitrageEngine:
    """
    Initialize and configure the arbitrage engine with all dependencies.

    Returns:
        ArbitrageEngine: Configured arbitrage engine instance

    Raises:
        ValueError: If configuration is invalid or required settings are missing
        RuntimeError: If connector initialization fails
    """
    try:
        # Load configuration from environment and config files
        settings = load_settings()
        logger.info("Configuration loaded successfully")

        # Initialize connectors
        logger.info("Initializing exchange connectors...")
        uniswap_connector = UniSwapConnector(
            network=settings.network,
            rpc_url=settings.rpc_url,
            timeout=settings.connector_timeout,
        )
        logger.debug("UniSwap connector initialized")

        sushiswap_connector = SushiSwapConnector(
            network=settings.network,
            rpc_url=settings.rpc_url,
            timeout=settings.connector_timeout,
        )
        logger.debug("SushiSwap connector initialized")

        # Initialize price aggregator
        logger.info("Initializing price aggregator...")
        price_aggregator = PriceAggregator(
            connectors=[uniswap_connector, sushiswap_connector],
            cache_ttl=settings.price_cache_ttl,
        )
        logger.debug("Price aggregator initialized")

        # Initialize notifier if configured
        notifier = None
        if settings.enable_notifications:
            logger.info("Initializing notifier...")
            notifier = Notifier(
                webhook_url=settings.webhook_url,
                notification_threshold=settings.profit_threshold,
            )
            logger.debug("Notifier initialized")

        # Initialize arbitrage engine
        logger.info("Initializing arbitrage engine...")
        engine = ArbitrageEngine(
            price_aggregator=price_aggregator,
            connectors=[uniswap_connector, sushiswap_connector],
            notifier=notifier,
            min_profit_threshold=settings.min_profit_threshold,
            gas_price_multiplier=settings.gas_price_multiplier,
            max_transaction_value=settings.max_transaction_value,
        )
        logger.debug("Arbitrage engine initialized")

        logger.info("Engine initialization completed successfully")
        return engine

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except RuntimeError as e:
        logger.error(f"Connector initialization failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during engine initialization: {e}", exc_info=True)
        raise


def main() -> NoReturn:
    """
    Main entry point for the arbitrage trading system.

    This function:
    1. Sets up logging
    2. Loads configuration
    3. Initializes the arbitrage engine
    4. Runs the arbitrage detection loop
    5. Handles graceful shutdown

    Raises:
        GracefulShutdown: When termination signal is received
    """
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting cryptocurrency arbitrage trading system")

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initialize the arbitrage engine
        engine = initialize_engine()

        # Run the arbitrage detection and execution loop
        logger.info("Starting arbitrage detection loop")
        engine.run()

    except GracefulShutdown:
        logger.info("Graceful shutdown completed")
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        sys.exit(0)
    except ValueError as e:
        logger.critical(f"Configuration validation failed: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.critical(f"Runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
