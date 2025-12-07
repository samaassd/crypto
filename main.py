import time
from connectors.uniswap import UniswapConnector
from connectors.sushiswap import SushiSwapConnector
from core.price_aggregator import PriceAggregator
from core.arbitrage_engine import ArbitrageEngine
from core.execution import TradeExecutor
from utils.notifier import send_telegram_message
from utils.helpers import get_eth_price
from config.settings import SCAN_INTERVAL

def main():
    connectors = [UniswapConnector(), SushiSwapConnector()]
    aggregator = PriceAggregator(connectors)
    engine = ArbitrageEngine(connectors)
    executor = TradeExecutor()
    token_pairs = [("ETH", "USDT"), ("ETH", "DAI")]
    
    while True:
        try:
            prices = aggregator.fetch_prices(token_pairs)
            opportunities = engine.find_opportunities(prices)
            
            if opportunities:
                eth_price_usd = get_eth_price()
                for opp in opportunities:
                    gas_cost_eth = 0.005
                    net_profit = opp["profit"] - (gas_cost_eth * eth_price_usd)
                    
                    if net_profit > 0:
                        msg = (f"Arbitrage Opportunity!\n"
                               f"Pair: {opp['pair']}\n"
                               f"Buy from: {opp['buy_from']} at lower price\n"
                               f"Sell to: {opp['sell_to']} for profit: {net_profit:.2f} USD")
                        print(msg)
                        send_telegram_message(msg)
            
            time.sleep(SCAN_INTERVAL)
            
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()