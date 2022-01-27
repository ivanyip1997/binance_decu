# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 00:49:17 2022

@author: Ivan
"""
import Trade
trade = Trade.execution_machine("DOGE", "1m") #to start the machine {asset(str), timeframe:{"1m","5m","15m","30m","1h","2h","4h","6h","8h","12h","1d"}}
trade.login() #login to Binance account {api_key , api_secret}

trade.ADTV_check() #check the ADTV and price of the asset

#trade.run("starting_price", "end_time", "sharesToDispos")   #!!!!Run the decu!!!!! {starting_price(float) , end_time(str in "%Y-%m-%d %H:%M"), sharesToDispos:{'all' or amount(float)}}

#trade.export_history("desktop") #exporting the deal record {location_of_export(path)}
