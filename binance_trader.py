import json,  math
from binance.client import Client

with open('config.json') as f:
  config = json.load(f)

binance_key=config['binance-api-key']
binance_secret=config['binance-api-secret']
client = Client(binance_key, binance_secret)

def getBalance():
    for a in client.futures_account_balance():
        if a['asset'] == 'USDT':
            return float(a['withdrawAvailable'])

def getQuantityPrecision(currency_symbol):    
    info = client.futures_exchange_info() 
    info = info['symbols']
    for x in range(len(info)):
        if info[x]['symbol'] == currency_symbol:
            return info[x]['quantityPrecision']
    return None

def placeOrder(symbol, entry, takeProfit, stopLoss, amountPercentage, leverage):
    order = {}
    balance = getBalance()
    # print(client.futures_get_open_orders(symbol="CHZUSDT"))
    symbols_n_precision = {}
    info = client.futures_exchange_info() # request info on all futures symbols
    for item in info['symbols']: 
        symbols_n_precision[item['symbol']] = item['quantityPrecision'] # not really necessary but here we are...

    trade_size_in_dollars = (balance * leverage) * amountPercentage

    price = client.futures_mark_price(symbol=symbol)['markPrice']

    order_amount = trade_size_in_dollars / float(price) # size of order in BTC

    precision = symbols_n_precision[symbol] # the binance-required level of precision

    precise_order_amount = "{:0.0{}f}".format(order_amount, precision) # string of precise order amount that can be used when creating order
    
    client.futures_change_leverage(symbol=symbol, leverage=leverage)

    buy_order_limit = client.futures_create_order(
        symbol=symbol,
        side='BUY',
        type='MARKET',
        quantity=precise_order_amount
        )

    takeProfitOrder = client.futures_create_order(
        symbol=symbol,
        side='SELL',
        type='TAKE_PROFIT_MARKET',
        stopPrice=float(takeProfit),
        closePosition=True
    )

    stopLossOrder = client.futures_create_order(
        symbol=symbol,
        side='SELL',
        type='STOP_MARKET',
        stopPrice=float(stopLoss),
        closePosition=True
    )

    print(f'PLACED ORDER\nSYMBOL: {symbol}\nAMOUNT: {trade_size_in_dollars}\nENTRY: {price}\nTP: {takeProfit}\nSL: {stopLoss}')

    order['symbol'] = symbol
    order['amount'] = trade_size_in_dollars
    order['entry'] = price
    order['tp'] = takeProfit
    order['sl'] = stopLoss

    return order

def main():
    print(client.futures_mark_price(symbol='BTCUSDT')['markPrice'])

if __name__ == "__main__":
    main()