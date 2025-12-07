from web3 import Web3
from config.settings import RPC_URL

class TradeExecutor:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(RPC_URL))

    def estimate_gas(self, tx):
        return self.web3.eth.estimate_gas(tx)

    def execute_trade(self, signed_tx):
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()