import yfinance as yf
import pandas as pd
import numpy as np
import datetime as dt
from pandas_datareader import data as pdr
from . import Option_Data as opt
import time

def get_put_data(input):
    print(input)
    stocklist = []
    if isinstance(input, list):
        for line in input:
            stocklist.append(line.strip())
    else:
        for line in input:
            line_str = line.decode('utf-8').strip()
            stocklist.append(line_str)
    option_data_all_puts = pd.DataFrame()
    print("length stocklist: ", len(stocklist))
    for stock in stocklist:
        try:
            option_data = opt.Option_Data(stock)
            option_data_all_puts = pd.concat([option_data_all_puts, option_data.all_otm_puts_df])
            print(f'Put Data Found for Ticker {stock}')
        except Exception as e:
            print(f'Problem Retrieving Data for Ticker {stock}')
            print(f'Error Message:{str(e)}')

    # option_data_all_puts.to_csv('./put_option_data.csv', index=False)
    return option_data_all_puts

def get_put_data_etf(input):
    stocklist = []
    with open(input) as f:
        for line in f:
            stocklist.append(line.strip())
    option_data_all_puts = pd.DataFrame()
    for stock in stocklist:
        try:
            option_data = opt.Option_Data(stock)
            option_data_all_puts = pd.concat([option_data_all_puts, option_data.all_otm_puts_df])
            print(f'Put Data Found for Ticker {stock}')
        except:
            print(f'Problem Retrieving Data for Ticker {stock}')

    option_data_all_puts.to_csv('./put_etf_option_data.csv', index=False)
def get_call_data(input):
    stocklist = []
    with open(input) as f:
        for line in f:
            stocklist.append(line.strip())
    option_data_all_calls = pd.DataFrame()
    for stock in stocklist:
        try:
            option_data = opt.Option_Data(stock)
            option_data_all_calls = pd.concat([option_data_all_calls, option_data.all_otm_calls_df])
            print(f'Call Data Found for Ticker {stock}')
        except:
            print(f'Problem Retrieving Data for Ticker {stock}')

    option_data_all_calls.to_csv('./call_option_data.csv', index=False)

def get_call_data_etf(input):
    stocklist = []
    with open(input) as f:
        for line in f:
            stocklist.append(line.strip())
    option_data_all_calls = pd.DataFrame()
    for stock in stocklist:
        try:
            option_data = opt.Option_Data(stock)
            option_data_all_calls = pd.concat([option_data_all_calls, option_data.all_otm_calls_df])
            print(f'Call Data Found for Ticker {stock}')
        except:
            print(f'Problem Retrieving Data for Ticker {stock}')

    option_data_all_calls.to_csv('./call_etf_option_data.csv', index=False)

# if __name__ == "__main__":
#     filepathpath_stocks = "Option_Stock_Sells.txt"
#     filpath_etf = "ETF_Tickers.txt"
#     start_time = time.time()
#     get_put_data(filepath_stocks)
#     get_call_data(filepath_stocks)
#     get_call_data_etf(filpath_etf)
#     get_put_data_etf(filpath_etf)
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Elapsed time: {elapsed_time} seconds")

