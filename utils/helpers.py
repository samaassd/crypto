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
