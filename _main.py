GRAPH_API_KEY = "b54919c92ed5aae4cdb961d4aa66bbb6"
import os
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_KEY = "b54919c954919c92ed5aae4cdb961d4aa66bbb6" 
UNISWAP_SUBGRAPH_URL = f"https://gateway-arbitrum.network.thegraph.com/api/{b54919c92ed5aae4cdb961d4aa66bbb6}/subgraphs/id/EYCKATKGBKLWvSfwvBjzfCBmGwYNdVkduYXVivCsLRFu"
SUSHISWAP_SUBGRAPH_URL = f"https://gateway-arbitrum.network.thegraph.com/api/{b54919c92ed5aae4cdb961d4aa66bbb6}/subgraphs/id/6NJWumPssRguR8a6HG79BFcGRzeGn36dSNpTHsk7FTUZ"
RPC_URL = os.getenv("RPC_URL=https://mainnet.infura.io/v3/4e9b931e3a844e72b50dac575ea991e5")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN=8433032915:AAFIPHeW65oRPhi4sM_o0V8oPR1AgI30kaQ")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID=6962891202")
SCAN_INTERVAL = 10  # seconds
# Environment Variables
RPC_URL = "https://mainnet.infura.io/v3/4e9b931e3a844e72b50dac575ea991e5"
TELEGRAM_TOKEN = "8433032915:AAFIPHeW65oRPhi4sM_o0V8oPR1AgI30kaQ"
TELEGRAM_CHAT_ID = "6962891202"
PRIVATE_KEY = "Vy5YGEp48IWH+Xtp7vqWBSZpF/3gxEGYZqjqqgf0Tko4jYPmktr7hQ"

# Environment Variables
RPC_URL = "https://mainnet.infura.io/v3/4e9b931e3a844e72b50dac575ea991e5"
TELEGRAM_TOKEN = "8433032915:AAFIPHeW65oRPhi4sM_o0V8oPR1AgI30kaQ"
TELEGRAM_CHAT_ID = "6962891202" 
PRIVATE_KEY = "Vy5YGEp48IWH+Xtp7vqWBSZpF/3gxEGYZqjqqgf0Tko4jYPmktr7hQ"

def calculate_profir(buy_price, sell_price, amount, gas_cost_eth, eth_price_usd):
    gross_profit = (sell_price - buy_price) * amount
    gas_cost_usd = gas_cost_eth * eth_price_usd
    net_profit = gross_profit - gas_cost_usd
    return net_profit

class BaseConnector:



    def __init__(self, name):
        self.name = name

    def get_price(self, token_in, token_out):
        raise NotImplementedError("Implement in subclass")

    def get_pairs(self):
        raise NotImplementedError("Implement in subclass")

    def execute_trade(self, token_in, token_out, amount):







        raise NotImplementedError("Implement in subclass")
    
    import requests
from config.settings import UNISWAP_SUBGRAPH_URL

PAIR_ADDRESSES = {
  ("ETH", "USDT"): "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852",
  ("ETH", "DAI"): "0xa478c2975ab1ea89e8196811f51a7b7ade33eb11",
}

class UniswapConnector:
  def __init__(self):
    self.name = "Uniswap"
    self.subgraph_url = UNISWAP_SUBGRAPH_URL

  def get_price(self, token_in, token_out):
    pair_key = (token_in, token_out)
    pair_address = PAIR_ADDRESSES.get(pair_key)
    
    if not pair_address:
      print(f"No pair address found for {token_in}/{token_out}")
      return None
    
    query = f"""
    {{{{
      pair(id: "{pair_address.lower()}") {{{{
      token0Price
      token1Price
      token0 {{{{ symbol }}}}
      token1 {{{{ symbol }}}}
      }}}}
    }}}}
    """
    
    try:
      response = requests.post(
        self.subgraph_url, 
        json={"query": query}, 
        timeout=10,
        headers={"Content-Type": "application/json"}
      )
      response.raise_for_status()
      data = response.json()
      
      if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None
      
      if "data" not in data:
        print(f"Warning: 'data' key not found in response")
        return None
      
      if "pair" not in data["data"] or data["data"]["pair"] is None:
        print(f"Warning: No pair data found for {token_in}/{token_out}")
        return None
      
      return float(data["data"]["pair"]["token0Price"])
      
    except requests.exceptions.RequestException as e:
      print(f"Uniswap API error for {token_in}/{token_out}: {e}")
      return None
    except (KeyError, TypeError, ValueError) as e:
      print(f"Uniswap data parsing error: {e}")
      return None
    
import requests
from config.settings import SUSHISWAP_SUBGRAPH_URL

PAIR_ADDRESSES = {
  ("ETH", "USDT"): "0x06da0fd433c1a5d7a4faa01111c044910a184553",
  ("ETH", "DAI"): "0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f",
}

class SushiSwapConnector:
  def __init__(self):
    self.name = "SushiSwap"
    self.subgraph_url = SUSHISWAP_SUBGRAPH_URL

  def get_price(self, token_in, token_out):
    pair_key = (token_in, token_out)
    pair_address = PAIR_ADDRESSES.get(pair_key)
    
    if not pair_address:
      print(f"No pair address found for {token_in}/{token_out}")
      return None
    
    query = f"""
    {{{{
      pair(id: "{pair_address.lower()}") {{{{
      token0Price
      token1Price
      token0 {{{{ symbol }}}}
      token1 {{{{ symbol }}}}
      }}}}
    }}}}
    """
    
    try:
      response = requests.post(
        self.subgraph_url,
        json={"query": query},
        timeout=10,
        headers={"Content-Type": "application/json"}
      )
      response.raise_for_status()
      data = response.json()
      
      if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return None
      
      if "data" not in data:
        print(f"Warning: 'data' key not found in response")
        return None
      
      if "pair" not in data["data"] or data["data"]["pair"] is None:
        print(f"Warning: No pair data found for {token_in}/{token_out}")
        return None
      
      return float(data["data"]["pair"]["token0Price"])
    
    except requests.exceptions.RequestException as e:
      print(f"Request error: {e}")
      return None
    except (KeyError, ValueError) as e:
      print(f"Error parsing response: {e}")
      return None
    
    from .base_connector import BaseConnector

class PancakeSwapConnector(BaseConnector):
    def __init__(self):
        super().__init__("PancakeSwap")

    def get_price(self, token_in, token_out):
        # Placeholder: Fetch from PancakeSwap API or The Graph
        return 1000.0  # Example price

    def get_pairs(self):
        return [("ETH", "USDT"), ("ETH", "DAI")]
    

def get_price(self, token_in_address, token_out_address):
    query = f"""
    {{
      pairs(where: {{
        token0: "{token_in_address.lower()}", 
        token1: "{token_out_address.lower()}"
      }}) {{
        token0Price
        token1Price
      }}
    }}
    """
    try:
        response = requests.post(PANCAKESWAP_SUBGRAPH, json={"query": query})
        data = response.json()

        if "data" in data and data["data"].get("pairs"):
            pair_data = data["data"]["pairs"][0]
            return float(pair_data["token0Price"])
        else:
            print(f"⚠️ No price found for {token_in_address}/{token_out_address} on Uniswap")
            return None
    except Exception as e:
        print(f"❌ Error fetching price: {e}")
        return None

class PriceAggregator:
    def __init__(self, connectors):
        self.connectors = connectors

    def fetch_prices(self, token_pairs):
        prices = {}
        for pair in token_pairs:
            token_in, token_out = pair
            prices[pair] = {}
            for connector in self.connectors:
                prices[pair][connector.name] = connector.get_price(token_in, token_out)
        return prices
    

class ArbitrageEngine:
    def __init__(self, connectors):
        self.connectors = connectors

    def find_opportunities(self, prices):
        opportunities = []
        for pair, dex_prices in prices.items():
            # Compare prices across DEXs
            dex_names = list(dex_prices.keys())
            for i in range(len(dex_names)):
                for j in range(i+1, len(dex_names)):
                    buy_dex = dex_names[i]
                    sell_dex = dex_names[j]
                    buy_price = dex_prices[buy_dex]
                    sell_price = dex_prices[sell_dex]

                    # Arbitrage calculation
                    profit = sell_price - buy_price
                    if profit > 5:  # Example threshold
                        opportunities.append({
                            "pair": pair,
                            "buy_from": buy_dex,
                            "sell_to": sell_dex,
                            "profit": profit
                        })
        return opportunities
    def execute_trade(self, opportunity):
        buy_dex = self.connectors[opportunity["buy_from"]]
        sell_dex = self.connectors[opportunity["sell_to"]]
        pair = opportunity["pair"]

        # Execute buy order
        buy_order = buy_dex.create_order(
            symbol=pair,
            type='market',
            side='buy',
            amount=1  # Example amount
        )

        # Execute sell order
        sell_order = sell_dex.create_order(
            symbol=pair,
            type='market',
            side='sell',
            amount=1  # Example amount
        )

        return {
            "buy_order": buy_order,
            "sell_order": sell_order
        }
    
    from web3 import Web3
from config.settings import RPC_URL


# Helper functions

def get_eth_price():
    pass

import requests

def get_eth_price():
    """
    Fetch ETH price in USD from Coingecko.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url).json()
        return response["ethereum"]["usd"]
    except Exception as e:
        print(f"❌ Failed to fetch ETH price: {e}")
        return None

# Logger utility
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ArbitrageBot')

import requests
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)

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

