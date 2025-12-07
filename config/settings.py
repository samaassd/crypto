
import os
from dotenv import load_dotenv

load_dotenv()

UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
RPC_URL = os.getenv("RPC_URL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCAN_INTERVAL = 30  # seconds