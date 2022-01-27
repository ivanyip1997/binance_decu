# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 23:37:15 2022

@author: Ivan
"""
from Live_Data import *
from datetime import datetime
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
import numpy as np
import schedule
import os

time_trans = {"1m":1, "5m":5, "15m":15, "30m":30,"1h":60, "2h":120, "4h":240, "6h":360, "8h":480, "12h":720, "1d": 1440}

class execution_machine:
    def __init__(self, asset, time_frame):
        #Mandatory input:
        self.asset = asset
        self.time_frame = time_frame
        #Optional input:
        self._ADTVLimit = 0.2
        self._SaleLimit = 0.0
        self.num_interval = 720
        self.data = []
        self.symbol = self.asset+"USDT"
        self.min_lot , self.min_price = get_min_selling_quo(self.symbol)

    #login
    def login(self):
        with open('key.txt','r') as f:
            lines = f.readlines()
        self.api_key = lines[0].replace("\n","").replace(" ","")
        self.api_secret = lines[1].replace("\n","").replace(" ","")
        self.client = Client(self.api_key, self.api_secret)
        self._current_stock = float(self.client.get_asset_balance(asset=self.asset)["free"])
        print(f"Remining balance of {self.asset}: {self._current_stock}")
    
    
    def DecumulatorMultiplier(self, _rtn, _MktADTV, _MktVol, _MDL, _S2D):
        _maxMultiplier = max(_MktADTV*self._ADTVLimit/_S2D, 2)
        if _MDL == 'TANH':
            _tp = np.arctanh((_maxMultiplier-2)/_maxMultiplier)/100
            _multiplier = (np.tanh((_rtn-_tp)*100)+1)/(np.tanh((0-_tp)*100)+1) if _rtn>=_SaleLimit else 0
            return _maxMultiplier, _tp, _multiplier
        elif _MDL == 'LOGI':
            _tp = np.log(_maxMultiplier-1)/100
            _multiplier = (np.exp(_tp*100)+1)/(np.exp(-(_rtn-_tp-_SaleLimit)*100)+1) if _rtn>=_SaleLimit else 0
            return _maxMultiplier, _tp, _multiplier
        else:
            return 0

    #ADTV Check
    def ADTV_check(self):
        print(self.symbol,":",sum([float(i[5]) for i in get_last_session_candle(self.symbol, self.time_frame, self.num_interval)])/self.num_interval)
        Bid_price,Ask_price = get_live_bid_ask(self.symbol, 5)
        print(f"current price of {self.symbol}: {Bid_price}")
     
    #Execution function
    def executor(self):
        candle_data = get_last_session_candle(self.symbol, self.time_frame, self.num_interval)    #get candle data
        ADTV = sum([float(i[5]) for i in candle_data])/self.num_interval
        close_price_list = [float(i[4]) for i in candle_data]        
        Bid_price,Ask_price = get_live_bid_ask(self.symbol, 5)
        period_return = [0] + list(np.diff(np.log(close_price_list)))              #calculte vol - 1
        Vol = np.sqrt((sum([r**2 for r in period_return])))                        #calculte vol - 2
        Return = (Bid_price-self.starting_price)/self.starting_price                         #Use bid price to calculate the return rate of this moment
        _maxMultiplier, _tp, _multiplier = self.DecumulatorMultiplier(Return, ADTV, Vol, "TANH", self._sharesToDispose)#Missing ADTV Limit
        sell_amount = round(((_multiplier*self.one_disposal)//self.min_lot)*self.min_lot,8)
        if _multiplier>0 and sell_amount*get_live_price(self.symbol)>=self.min_price:
            if self._sharesToDispose_temp>=sell_amount:
                self.data+=[[datetime.now(),sell_amount, ADTV, Bid_price, Vol, Return, _multiplier, _tp, _maxMultiplier]]
                self._sharesToDispose_temp-=sell_amount
                try:
                    order = self.client.order_market_sell(symbol=self.symbol,quantity=sell_amount)
                    print(order)
                except BinanceAPIException as e:
                    print(e)
            elif self._sharesToDispose_temp<sell_amount and round(((self._sharesToDispose_temp)//self.min_lot)*self.min_lot,8)*get_live_price(self.symbol)>=self.min_price:
                sell_amount = round(((self._sharesToDispose_temp)//self.min_lot)*self.min_lot,8)
                try:
                    order = self.client.order_market_sell(symbol=self.symbol,quantity=sell_amount)
                    print(order)
                except BinanceAPIException as e:
                    print(e)
                self.data+=[[datetime.now(),sell_amount, ADTV, Bid_price, Vol, Return, _multiplier, _tp, _maxMultiplier]]
                self._sharesToDispose_temp=0
        else:
            self.data+=[[datetime.now(),0, ADTV, Bid_price, Vol, Return, _multiplier, _tp, _maxMultiplier]]
            
    #Run
    def run(self, starting_price, end_time, sharesToDispose):
        if sharesToDispose=="all":
            self._sharesToDispose = self._current_stock
        else:
            self._sharesToDispose = float(sharesToDispose)
        self.starting_price = starting_price
        self.end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        self._sharesToDispose_temp = self._sharesToDispose
        self.total_sec = (self.end_time-datetime.now()).total_seconds()#calculate the number of seconds within the period
        self.one_disposal = self._sharesToDispose/((self.total_sec/60)/time_trans[self.time_frame])
        schedule.every(time_trans[self.time_frame]).minutes.do(self.executor)
        while datetime.now()<self.end_time:
            schedule.run_pending()

    def export_history(self, location):
        self.data.to_excel(os.path.join(location,"Deal_records.xlsx"),index=0)
    


