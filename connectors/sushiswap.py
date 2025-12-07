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