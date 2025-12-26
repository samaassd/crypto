# Blockchain Configuration
BLOCKCHAIN_NETWORK = "ethereum"
BLOCKCHAIN_RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
BLOCKCHAIN_CHAIN_ID = 1

# Token Pairs Configuration for Arbitrage Bot
TOKEN_PAIRS = [
    ("ETH", "USDT"),
    ("ETH", "DAI"),
    ("USDT", "USDC"),
    ("DAI", "USDC"),
]

# Token Pair Addresses Configuration
# Maps token pairs to their contract addresses for different chains
TOKEN_PAIR_ADDRESSES = {
    "ethereum": {
        ("ETH", "USDT"): {
            "ETH": "0xC02aaA39b223FE8D0A0e8e4F27ead9083C756Cc2",  # WETH
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        },
        ("ETH", "DAI"): {
            "ETH": "0xC02aaA39b223FE8D0A0e8e4F27ead9083C756Cc2",  # WETH
            "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        },
        ("USDT", "USDC"): {
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        },
        ("DAI", "USDC"): {
            "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        },
    },
    "polygon": {
        ("ETH", "USDT"): {
            "ETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",  # WETH
            "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        },
        ("ETH", "DAI"): {
            "ETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",  # WETH
            "DAI": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023D60d76546",
        },
    },
}
