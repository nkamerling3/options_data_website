import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
import re
import yahoo_fin.stock_info as si
import requests
from bs4 import BeautifulSoup
from scipy.stats import norm


class Option_Data(object):
    """
    This class finds the options prices of a stock at different strikes
    """

    def __init__(self, stock_name):
        """
        Constructor method
        """
        self.all_otm_puts_df = pd.DataFrame()
        self.all_otm_calls_df = pd.DataFrame()
        stock = yf.Ticker(stock_name)
        yf.pdr_override()
        expiration_dates = stock.options
        now = dt.datetime.now()
        three_days_ago = now - dt.timedelta(days=3)
        price_df = pdr.get_data_yahoo(stock_name, three_days_ago, now)
        currentPrice = price_df['Adj Close'].iloc[-1]

        earnings_dates = stock.get_earnings_dates()
        if earnings_dates is not None:
            earnings_dates.index = earnings_dates.index.tz_convert(None)

            future_earnings_dates = earnings_dates[earnings_dates.index > now]
            if future_earnings_dates.shape[0] < 1:
                earnings_string = 'No Earnings Available'
                next_earnings_date = now
            else:
                next_earnings_date = future_earnings_dates.index[-1]
                earnings_string = next_earnings_date.strftime('%m/%d/%y')
        else:
            earnings_string = 'No Earnings Available'
            next_earnings_date = now

        for date in expiration_dates:
            option_chain = stock.option_chain(date)
            puts = option_chain.puts
            calls = option_chain.calls
            otm_puts = puts[puts['inTheMoney'] == False]
            otm_calls = calls[calls['inTheMoney'] == False]
            self.all_otm_puts_df = pd.concat([self.all_otm_puts_df, otm_puts], ignore_index=True)
            self.all_otm_calls_df = pd.concat([self.all_otm_calls_df, otm_calls], ignore_index=True)
            # columns for df: earnings and if expiration is after earnings, dte, collateral required, return as a
            # percent, and annualized return, stock price, delta,

        # Add price and company name, price, expiration after earnings, dte, collateral required, return as a percent,
        # annualized return, delta to df and rearrange df
        self.all_otm_puts_df['Stock Price'] = currentPrice
        self.all_otm_calls_df['Stock Price'] = currentPrice
        self.all_otm_puts_df['Ticker'] = stock_name
        self.all_otm_calls_df['Ticker'] = stock_name
        self.all_otm_puts_df['Expiration Date'] = (self.all_otm_puts_df['contractSymbol'].
                                                   apply(lambda x: self.extract_and_format_date(x)))
        self.all_otm_calls_df['Expiration Date'] = (self.all_otm_calls_df['contractSymbol'].
                                                    apply(lambda x: self.extract_and_format_date(x)))

        self.all_otm_puts_df['DTE'] = (pd.to_datetime(self.all_otm_puts_df['Expiration Date'], format="%m/%d/%y")
                                       - dt.datetime.now()).dt.days + 1
        self.all_otm_calls_df['DTE'] = (pd.to_datetime(self.all_otm_calls_df['Expiration Date'], format="%m/%d/%y")
                                        - dt.datetime.now()).dt.days + 1

        self.all_otm_puts_df['Earnings Date'] = earnings_string
        self.all_otm_calls_df['Earnings Date'] = earnings_string

        self.all_otm_puts_df['Expiration Date dt'] = (pd.to_datetime(self.all_otm_puts_df['Expiration Date'],
                                                                     format="%m/%d/%y"))
        self.all_otm_calls_df['Expiration Date dt'] = (pd.to_datetime(self.all_otm_calls_df['Expiration Date'],
                                                                      format="%m/%d/%y"))

        self.all_otm_puts_df['Expiration Before Earnings'] = np.where(self.all_otm_puts_df['Earnings Date'] ==
                                                                      'No Earnings Available', 'N/A',
                                                                      np.where(
                                                                          self.all_otm_puts_df['Expiration Date dt'] >=
                                                                          next_earnings_date, 'No', 'Yes'))
        self.all_otm_calls_df['Expiration Before Earnings'] = np.where(self.all_otm_calls_df['Earnings Date'] ==
                                                                       'No Earnings Available', 'N/A',
                                                                       np.where(
                                                                          self.all_otm_calls_df['Expiration Date dt'] >=
                                                                          next_earnings_date, 'No', 'Yes'))

        interest_rate = 0.0526
        self.all_otm_puts_df['Delta'] = self.calculate_black_scholes_delta_sell(
            self.all_otm_puts_df['Stock Price'],
            self.all_otm_puts_df['strike'],
            interest_rate,
            self.all_otm_puts_df['DTE']/365,
            self.all_otm_puts_df['impliedVolatility'],
            option_type='put'
        )
        self.all_otm_calls_df['Delta'] = self.calculate_black_scholes_delta_sell(
            self.all_otm_calls_df['Stock Price'],
            self.all_otm_calls_df['strike'],
            interest_rate,
            self.all_otm_calls_df['DTE']/365,
            self.all_otm_calls_df['impliedVolatility'],
            option_type='call'
        )

        self.all_otm_puts_df['Collateral Required'] = self.all_otm_puts_df['strike'] * 100
        self.all_otm_puts_df['Return on Collateral'] = (self.all_otm_puts_df['bid'] * 100) / self.all_otm_puts_df['Collateral Required']
        self.all_otm_puts_df['Annualized Return'] = self.all_otm_puts_df['Return on Collateral'] * 365 / self.all_otm_puts_df['DTE']
        self.all_otm_calls_df['Collateral Required'] = self.all_otm_calls_df['strike'] * 100
        self.all_otm_calls_df['Return on Collateral'] = (self.all_otm_calls_df['bid'] * 100) / self.all_otm_calls_df['Collateral Required']
        self.all_otm_calls_df['Annualized Return'] = self.all_otm_calls_df['Return on Collateral'] * 365 / self.all_otm_calls_df['DTE']



        desired_columns = ['Ticker', 'strike', 'Stock Price', 'Expiration Date', 'DTE', 'Earnings Date',
                           'Expiration Before Earnings', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility',
                           'Delta', 'Return on Collateral', 'Annualized Return']
        self.all_otm_puts_df = self.all_otm_puts_df[desired_columns]
        self.all_otm_calls_df = self.all_otm_calls_df[desired_columns]

    def extract_and_format_date(self, option_string):
        date_part = re.search(r'\d{6}', option_string).group()
        date_obj = dt.datetime.strptime(date_part, "%y%m%d")
        formatted_date = date_obj.strftime("%m/%d/%y")
        return formatted_date

    def calculate_black_scholes_delta_sell(self, S, K, r, T, sigma, option_type='call'):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if option_type == 'call':
            return norm.cdf(d1) * -1
        elif option_type == 'put':
            return (norm.cdf(d1) - 1) * -1
