import re, requests, json, asyncio, time
from datetime import datetime
from telethon import TelegramClient, events
import binance_trader as trader

with open('config.json') as f:
  config = json.load(f)

api_id=config['app_id']
api_hash=config['app_hash']
channel = config['input_channel']
receiver=config['output_channel']
keyword=config['keyword']
api_url=config['api_url']
api_token=config['api_token']
phone=config['phone']
password=config['password']
binance_key=config['binance-api-key']
binance_secret=config['binance-api-secret']

client = TelegramClient('telegramlistener', api_id, api_hash)

def getSymbol(s):
    symbol = s[s.index('#')+1 : s.index(' ')] 
    symbol = symbol.replace('_', '')
    return symbol

def getTakeProfitTargets(s):
    print(s)
    s = s[s.index(':') + 1 : len(s)]
    s = s.split('-')
    return (float(s[1]) + float(s[2]))/2

def getStopLossPrice(s):
    return s.split(' ')[6]

@client.on(events.NewMessage(chats=channel))
async def listen(event):
    signalMessage = event.message.message
    subjectFiltered = re.findall(keyword, signalMessage, re.IGNORECASE)
    if len(subjectFiltered) != 0:
        signalMessage = signalMessage.split('\n')
        symbol = getSymbol(signalMessage[0])
        takeProfit = getTakeProfitTargets(signalMessage[4])
        stopLoss = getStopLossPrice(signalMessage[6])

        order = trader.placeOrder(
            symbol=symbol,
            entry=None,
            takeProfit=takeProfit,
            stopLoss=stopLoss,
            amountPercentage = 0.1,
            leverage=25)
        amount = order['amount']
        entry = order['entry']
        message = f'PLACED ORDER\n\nSYMBOL: {symbol}\nAMOUNT: {amount}\nENTRY: {entry}\nTP: {takeProfit}\nSL: {stopLoss}'

        await client.send_message(receiver, message)

def main():
    client.start()
    client.run_until_disconnected()

if __name__ == "__main__":
    print("LISTENING")
    main()