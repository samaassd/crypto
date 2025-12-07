import requests
from config.settings.py import UNISWAP_SUBGRAPH_URL

PAIR_ADDRESSES = {
  ("ETH", "USDT"): "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852",
  ("ETH", "DAI"): "0xa478c2975ab1ea89e8196811f51a7b7ade33eb11",
}


class UniswapConnector:
  def __init__(self):
    self.name = "Uniswap"
    self.subgraph_url = UNISWAP_SUBGRAPH_URL

  def get_price(self, token_in, token_out):
    """Fetch price from Uniswap subgraph"""
    pair_key = (token_in, token_out)
    pair_address = PAIR_ADDRESSES.get(pair_key)

    if not pair_address:
      print(f"No pair address found for {token_in}/{token_out}")
      return None

    query = f"""
    {{
      pair(id: "{pair_address.lower()}") {{
      token0Price
      token1Price
      token0 {{ symbol }}
      token1 {{ symbol }}
      }}
    }}
    """

    try:
      response = requests.post(
        self.subgraph_url,
        json={"query": query},
        timeout=10
      )
      response.raise_for_status()
      data = response.json()

      print(f"Uniswap response for {token_in}/{token_out}: {data}")

      if "data" not in data:
        print(f"Warning: 'data' key not found in response: {data}")
        return None

      if "pair" not in data["data"] or data["data"]["pair"] is None:
        print(f"Warning: No pair data found for {token_in}/{token_out}")
        return None

      return float(data["data"]["pair"]["token0Price"])

    except requests.exceptions.RequestException as e:
      print(f"Uniswap API error for {token_in}/{token_out}: {e}")
      return None
    except (KeyError, TypeError, ValueError) as e:
      print(f"Uniswap data parsing error for {token_in}/{token_out}: {e}")
      return None