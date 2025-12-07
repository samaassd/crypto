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
    