import time
import logging
import signal
import sys
import traceback
from typing import List, Dict, Optional, Any
from connectors.uniswap import UniswapConnector
from connectors.sushiswap import SushiSwapConnector
from core.price_aggregator import PriceAggregator
from core.arbitrage_engine import ArbitrageEngine
from core.execution import TradeExecutor
from utils.notifier import send_telegram_message
from utils.helpers import get_eth_price, get_gas_price
from config.settings import SCAN_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arbitrage_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global shutdown event
shutdown_event = False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_event
    logger.info(f"Received signal {signum}. Shutting down gracefully...")
    shutdown_event = True

def fetch_dynamic_gas_cost(executor: TradeExecutor) -> float:
    """Fetch current gas cost from network or estimate conservatively"""
    try:
        gas_cost_eth = executor.get_current_gas_cost()
        logger.debug(f"Fetched dynamic gas cost: {gas_cost_eth} ETH")
        return gas_cost_eth
    except Exception as e:
        logger.warning(f"Failed to fetch dynamic gas cost: {e}. Using conservative estimate.")
        return 0.01  # Conservative fallback estimate

def validate_opportunity(opp: Dict[str, Any]) -> bool:
    """Validate that opportunity dict has all required fields"""
    required_fields = ['profit', 'pair', 'buy_from', 'sell_to', 'amount']
    
    for field in required_fields:
        if field not in opp:
            logger.error(f"Opportunity missing required field: {field}. Data: {opp}")
            return False
    
    # Validate data types
    if not isinstance(opp['profit'], (int, float)):
        logger.error(f"Profit must be numeric, got {type(opp['profit'])}")
        return False
    
    if not isinstance(opp['pair'], str):
        logger.error(f"Pair must be string, got {type(opp['pair'])}")
        return False
    
    return True

def execute_trade_safely(
    executor: TradeExecutor,
    opp: Dict[str, Any],
    gas_cost_eth: float,
    eth_price_usd: float
) -> bool:
    """Execute trade with proper error handling and validation"""
    try:
        # Calculate total costs
        slippage_buffer = 0.02  # 2% slippage buffer
        total_cost_usd = (gas_cost_eth * eth_price_usd) + (opp['profit'] * slippage_buffer)
        net_profit = opp['profit'] - total_cost_usd
        
        if net_profit <= 0:
            logger.info(f"Opportunity {opp['pair']} not profitable after slippage and gas: {net_profit:.2f} USD")
            return False
        
        logger.info(f"Executing trade for {opp['pair']}: {opp['amount']} units")
        logger.debug(f"Buy from: {opp['buy_from']}, Sell to: {opp['sell_to']}")
        
        # Execute the trade
        result = executor.execute_trade(
            pair=opp['pair'],
            amount=opp['amount'],
            buy_exchange=opp['buy_from'],
            sell_exchange=opp['sell_to']
        )
        
        if result and result.get('success', False):
            logger.info(f"Trade executed successfully for {opp['pair']}")
            logger.debug(f"Transaction hash: {result.get('tx_hash', 'N/A')}")
            return True
        else:
            logger.error(f"Trade execution failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Error executing trade: {e}", exc_info=True)
        return False

def main():
    """Main arbitrage bot loop"""
    global shutdown_event
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Arbitrage Bot...")
    
    try:
        # Initialize components
        connectors = [UniswapConnector(), SushiSwapConnector()]
        aggregator = PriceAggregator(connectors)
        engine = ArbitrageEngine(connectors)
        executor = TradeExecutor()
        
        token_pairs = [("ETH", "USDT"), ("ETH", "DAI")]
        logger.info(f"Monitoring {len(token_pairs)} token pairs: {token_pairs}")
        
        scan_cycle = 0
        opportunities_found = 0
        trades_executed = 0
        
        while not shutdown_event:
            scan_cycle += 1
            try:
                logger.debug(f"Starting scan cycle {scan_cycle}")
                
                # Fetch prices with error handling
                try:
                    prices = aggregator.fetch_prices(token_pairs)
                    logger.debug(f"Fetched prices for {len(prices)} pairs")
                except Exception as e:
                    logger.error(f"Failed to fetch prices: {e}", exc_info=True)
                    time.sleep(SCAN_INTERVAL)
                    continue
                
                # Find opportunities with error handling
                try:
                    opportunities = engine.find_opportunities(prices)
                    logger.debug(f"Found {len(opportunities)} potential opportunities")
                except Exception as e:
                    logger.error(f"Failed to find opportunities: {e}", exc_info=True)
                    time.sleep(SCAN_INTERVAL)
                    continue
                
                if opportunities:
                    opportunities_found += len(opportunities)
                    
                    # Fetch current prices for cost calculation
                    try:
                        eth_price_usd = get_eth_price()
                        logger.debug(f"Current ETH price: ${eth_price_usd:.2f}")
                    except Exception as e:
                        logger.error(f"Failed to fetch ETH price: {e}", exc_info=True)
                        eth_price_usd = 2000  # Conservative fallback
                    
                    # Get dynamic gas cost
                    gas_cost_eth = fetch_dynamic_gas_cost(executor)
                    
                    # Process each opportunity
                    for opp in opportunities:
                        # Validate opportunity structure
                        if not validate_opportunity(opp):
                            continue
                        
                        # Calculate net profit accounting for all costs
                        slippage_buffer = 0.02
                        total_cost_usd = (gas_cost_eth * eth_price_usd) + (opp['profit'] * slippage_buffer)
                        net_profit = opp['profit'] - total_cost_usd
                        
                        if net_profit > 0:
                            msg = (
                                f"🚀 Arbitrage Opportunity Found!\n"
                                f"Pair: {opp['pair']}\n"
                                f"Amount: {opp['amount']} units\n"
                                f"Buy from: {opp['buy_from']}\n"
                                f"Sell to: {opp['sell_to']}\n"
                                f"Gross Profit: ${opp['profit']:.2f} USD\n"
                                f"Gas Cost: ${gas_cost_eth * eth_price_usd:.2f} USD\n"
                                f"Slippage Buffer (2%): ${opp['profit'] * slippage_buffer:.2f} USD\n"
                                f"🎯 Net Profit: ${net_profit:.2f} USD"
                            )
                            logger.info(msg)
                            
                            try:
                                send_telegram_message(msg)
                            except Exception as e:
                                logger.warning(f"Failed to send Telegram notification: {e}")
                            
                            # Execute the trade
                            if execute_trade_safely(executor, opp, gas_cost_eth, eth_price_usd):
                                trades_executed += 1
                        else:
                            logger.debug(
                                f"Opportunity {opp['pair']} not profitable after costs. "
                                f"Net profit: ${net_profit:.2f}"
                            )
                
                logger.debug(f"Scan cycle {scan_cycle} complete. Sleeping for {SCAN_INTERVAL}s")
                time.sleep(SCAN_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in scan cycle {scan_cycle}: {e}", exc_info=True)
                logger.debug(f"Full traceback: {traceback.format_exc()}")
                time.sleep(SCAN_INTERVAL)
        
        # Shutdown summary
        logger.info("=" * 50)
        logger.info("Arbitrage Bot Shutdown Summary")
        logger.info(f"Total scan cycles: {scan_cycle}")
        logger.info(f"Total opportunities found: {opportunities_found}")
        logger.info(f"Total trades executed: {trades_executed}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.critical(f"Critical error in main loop: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()