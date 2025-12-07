import requests
from .base_connector import BaseConnector

SUSHISWAP_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/sushiswap/exchange"

class SushiSwapConnector(BaseConnector):
  def __init__(self):
    super().__init__("SushiSwap")

  def get_price(self, token_in, token_out):
    query = """
    {
      pair(id: "PAIR_ID") {
      token0Price
      token1Price
      }
    }
    """
    response = requests.post(SUSHISWAP_SUBGRAPH, json={"query": query})
    data = response.json()
    return float(data["data"]["pair"]["token0Price"])

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
        response = requests.post(SUSHISWAP_SUBGRAPH, json={"query": query})
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
