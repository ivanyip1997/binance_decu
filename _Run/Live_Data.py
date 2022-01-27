# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 22:25:55 2021

@author: Ivan
"""

#live price
import json
import requests
from datetime import datetime, timedelta

#Get live price
def get_live_price(symbol):
    return float(requests.get(f"https://api.binance.com/api/v3/avgPrice?symbol={symbol}").json()["price"])
#print(get_live_price('BTCUSDT'))

#Get last interval volumn, price...
def get_last_session_candle(symbol, tick_interval, session_num): #tick_interval:str([1m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d])
    tick_interval_trans={"1m":1, "5m":5, "15m":15, "30m":30,"1h":60, "2h":120, "4h":240, "6h":360, "8h":480, "12h":720, "1d": 1440}
    now = datetime.now()- timedelta(minutes=tick_interval_trans[tick_interval]*(session_num+1)) #take exact -1m to now
    startTime=int(datetime.timestamp(now))*1000 
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tick_interval}&limit=1000&startTime={startTime}'
    return requests.get(url).json()[0:-1]
#print(get_last_session_candle('BTCUSDT', '4h',30))
#-> ["Open time","Open","High","Low","Close","Volume","Close time", "Quote asset volume","Number of trades","Taker buy base asset volume","Taker buy quote asset volume","Ignore"]

#Get live bid ask price and qty
def get_live_bid_ask(symbol, limit): #limit: Default 100; max 5000. Valid limits:[5, 10, 20, 50, 100, 500, 1000, 5000]
    url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={str(limit)}'
    return float(requests.get(url).json()['bids'][0][0]), float(requests.get(url).json()['asks'][0][0])

def get_min_selling_quo(symbol):
    url = f"https://api.binance.com/api/v3/exchangeInfo?symbol={symbol}"
    return float(requests.get(url).json()['symbols'][0]['filters'][2]['minQty']) , float(requests.get(url).json()['symbols'][0]['filters'][3]['minNotional'])

get_min_selling_quo('ETHUSDT')
#bid, ask = get_live_bid_ask('BTCUSDT', 10)
#print(bid) #PRICE,QTY
#print(ask) #PRICE,QTY