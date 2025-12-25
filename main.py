import asyncio
import logging
import threading
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import sys
import os

# Import configuration and dependencies
try:
    from config import settings
    from connector import Connector
    from engine import Engine
    from exchange import Exchange
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Configure logging with rotation
def setup_logging():
    """Setup logging with rotating file handler"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "crypto_bot.log")
    
    # Use RotatingFileHandler for log rotation
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    # Also log to console
    console_handler = logging.getHandler()
    if not console_handler:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Thread-safe shutdown event using threading.Event()
shutdown_event = threading.Event()

# Global variables for connector and engine
connector = None
engine = None
exchange = None


def validate_config():
    """Validate that all required config values are valid before use"""
    try:
        # Check SCAN_INTERVAL
        if not hasattr(settings, 'SCAN_INTERVAL') or settings.SCAN_INTERVAL <= 0:
            raise ValueError(f"Invalid SCAN_INTERVAL: {getattr(settings, 'SCAN_INTERVAL', 'not set')}")
        
        # Check other critical settings
        if not hasattr(settings, 'PROFIT_THRESHOLD') or settings.PROFIT_THRESHOLD <= 0:
            raise ValueError(f"Invalid PROFIT_THRESHOLD: {getattr(settings, 'PROFIT_THRESHOLD', 'not set')}")
        
        # Validate token pairs exist in config
        if not hasattr(settings, 'TOKEN_PAIRS') or not settings.TOKEN_PAIRS:
            raise ValueError("TOKEN_PAIRS not configured in settings")
        
        logger.info("Configuration validation passed")
        return True
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def get_eth_price():
    """
    Fetch ETH price with input validation
    Returns float or None if validation fails
    """
    try:
        if exchange is None:
            logger.error("Exchange not initialized")
            return None
        
        price = exchange.get_price("ETH")
        
        # Validate return value before using in calculations
        if price is None:
            logger.error("ETH price returned None")
            return None
        
        if not isinstance(price, (int, float)):
            logger.error(f"Invalid price type: {type(price)}, expected numeric value")
            return None
        
        if price <= 0:
            logger.error(f"Invalid price value: {price}, must be positive")
            return None
        
        logger.info(f"ETH price: ${price}")
        return price
    
    except Exception as e:
        logger.error(f"Error fetching ETH price: {e}")
        return None


def initialize_connector_and_engine():
    """
    Initialize connector and engine with proper error handling
    Returns tuple: (connector, engine, exchange) or (None, None, None) on failure
    """
    global connector, engine, exchange
    
    try:
        logger.info("Initializing connector...")
        connector = Connector()
        
        logger.info("Initializing engine...")
        engine = Engine()
        
        logger.info("Initializing exchange...")
        exchange = Exchange()
        
        logger.info("All components initialized successfully")
        return connector, engine, exchange
    
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        # Cleanup any partially initialized components
        cleanup_resources()
        return None, None, None


def cleanup_resources():
    """
    Graceful cleanup function for shutdown with proper resource cleanup
    """
    global connector, engine, exchange
    
    logger.info("Starting graceful shutdown...")
    
    try:
        if engine is not None:
            logger.info("Closing engine...")
            engine.close()
            engine = None
    except Exception as e:
        logger.error(f"Error closing engine: {e}")
    
    try:
        if connector is not None:
            logger.info("Closing connector...")
            connector.close()
            connector = None
    except Exception as e:
        logger.error(f"Error closing connector: {e}")
    
    try:
        if exchange is not None:
            logger.info("Closing exchange...")
            exchange.close()
            exchange = None
    except Exception as e:
        logger.error(f"Error closing exchange: {e}")
    
    logger.info("Graceful shutdown completed")


def execute_trade_safely(token_pair, price, quantity):
    """
    Execute trade with proper error handling and validation
    Fixed profit calculation logic to not double-count profit with slippage
    
    Args:
        token_pair: The trading pair (e.g., "ETH/USDC")
        price: Current price of the token
        quantity: Quantity to trade
    
    Returns:
        bool: True if trade was successful, False otherwise
    """
    try:
        # Input validation
        if price is None or not isinstance(price, (int, float)) or price <= 0:
            logger.error(f"Invalid price: {price}")
            return False
        
        if quantity is None or not isinstance(quantity, (int, float)) or quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}")
            return False
        
        if not isinstance(token_pair, str) or not token_pair:
            logger.error(f"Invalid token pair: {token_pair}")
            return False
        
        # Calculate costs with null checks
        try:
            entry_price = float(price)
            order_quantity = float(quantity)
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to convert price/quantity to float: {e}")
            return False
        
        # Fixed: Calculate total cost without double-counting profit with slippage
        total_cost_usd = entry_price * order_quantity
        
        # Apply slippage factor (typically 0.5% - 1%)
        slippage_percentage = getattr(settings, 'SLIPPAGE_PERCENTAGE', 0.005)
        slippage_amount = total_cost_usd * slippage_percentage
        actual_cost = total_cost_usd + slippage_amount
        
        # Profit calculation (profit is separate from slippage, not combined)
        profit_threshold = getattr(settings, 'PROFIT_THRESHOLD', 0.02)
        expected_profit = (total_cost_usd * profit_threshold)
        
        logger.info(
            f"Executing trade for {token_pair}: "
            f"Price=${entry_price}, Quantity={order_quantity}, "
            f"Total Cost=${total_cost_usd:.2f}, Slippage=${slippage_amount:.2f}, "
            f"Actual Cost=${actual_cost:.2f}, Expected Profit=${expected_profit:.2f}"
        )
        
        # Execute the trade
        if engine is None:
            logger.error("Engine not initialized for trade execution")
            return False
        
        result = engine.execute_trade(token_pair, order_quantity, entry_price)
        
        if result:
            logger.info(f"Trade executed successfully for {token_pair}")
            return True
        else:
            logger.warning(f"Trade execution failed for {token_pair}")
            return False
    
    except Exception as e:
        logger.error(f"Error executing trade for {token_pair}: {e}")
        return False


async def scan_prices():
    """
    Main price scanning loop with thread-safe shutdown event
    Loads token pairs from config.settings
    """
    try:
        # Load token pairs from config.settings
        token_pairs = getattr(settings, 'TOKEN_PAIRS', [])
        
        if not token_pairs:
            logger.error("No token pairs configured in settings")
            shutdown_event.set()
            return
        
        logger.info(f"Starting price scan with token pairs: {token_pairs}")
        
        scan_interval = getattr(settings, 'SCAN_INTERVAL', 60)
        
        # Continue scanning while shutdown_event is not set (thread-safe)
        while not shutdown_event.is_set():
            try:
                logger.debug(f"Scanning {len(token_pairs)} token pairs...")
                
                for token_pair in token_pairs:
                    if shutdown_event.is_set():
                        break
                    
                    # Get ETH price with validation
                    eth_price = get_eth_price()
                    
                    if eth_price is None:
                        logger.warning(f"Could not fetch price for {token_pair}")
                        continue
                    
                    # Check if profitable and execute trade
                    profit_threshold = getattr(settings, 'PROFIT_THRESHOLD', 0.02)
                    
                    if eth_price > 0:  # Null check and type validation
                        # Determine quantity based on available balance
                        available_balance = connector.get_balance()
                        
                        if available_balance is None or not isinstance(available_balance, (int, float)):
                            logger.warning("Invalid balance returned from connector")
                            continue
                        
                        if available_balance > 0:
                            quantity = available_balance / eth_price
                            
                            # Execute trade with validation
                            execute_trade_safely(token_pair, eth_price, quantity)
                
                # Wait for next scan interval with shutdown check
                logger.debug(f"Next scan in {scan_interval} seconds...")
                await asyncio.sleep(scan_interval)
            
            except Exception as e:
                logger.error(f"Error during price scan: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
        
        logger.info("Price scanning stopped")
    
    except Exception as e:
        logger.error(f"Fatal error in scan_prices: {e}")
        shutdown_event.set()


async def main():
    """Main entry point for the crypto trading bot"""
    logger.info("=" * 60)
    logger.info("Starting Crypto Trading Bot")
    logger.info(f"Timestamp: {datetime.now()}")
    logger.info("=" * 60)
    
    # Validate configuration before proceeding
    if not validate_config():
        logger.error("Configuration validation failed. Exiting.")
        return
    
    # Initialize connector, engine, and exchange with proper error handling
    global connector, engine, exchange
    connector, engine, exchange = initialize_connector_and_engine()
    
    if connector is None or engine is None or exchange is None:
        logger.error("Failed to initialize required components. Exiting.")
        cleanup_resources()
        return
    
    try:
        # Run the main scanning loop
        await scan_prices()
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    
    finally:
        # Ensure proper cleanup
        shutdown_event.set()
        cleanup_resources()
        logger.info("Bot shutdown complete")


def signal_shutdown():
    """Signal the bot to shutdown gracefully"""
    logger.info("Shutdown signal received")
    shutdown_event.set()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
