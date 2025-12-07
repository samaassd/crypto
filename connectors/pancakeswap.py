from .base_connector import BaseConnector

class PancakeSwapConnector(BaseConnector):
    def __init__(self):
        super().__init__("PancakeSwap")

    def get_price(self, token_in token_out):
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

