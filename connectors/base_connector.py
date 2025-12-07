class BaseConnector:



    def __init__(self, name):
        self.name = name

    def get_price(self, token_in, token_out):
        raise NotImplementedError("Implement in subclass")

    def get_pairs(self):
        raise NotImplementedError("Implement in subclass")

    def execute_trade(self, token_in, token_out, amount):







        raise NotImplementedError("Implement in subclass")