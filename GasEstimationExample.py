def calculate_profir(buy_price, sell_price, amount, gas_cost_eth, eth_price_usd):
    gross_profit = (sell_price - buy_price) * amount
    gas_cost_usd = gas_cost_eth * eth_price_usd
    net_profit = gross_profit - gas_cost_usd
    return net_profit
