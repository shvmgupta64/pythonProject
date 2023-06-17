#***************************************************************************
#
#This class is created to manager dataframes.
#all the operations related to data frames, will be conducted in this class.
#
#
#**************************************************************************

import pandas as pd
import numpy
import datetime

class RSIManager:

    def __init__(self):
        pass

    # Calculate Supertrend indicator
    def calculate_rsi(self, df, window=14):
        """
        Calculate the Relative Strength Index (RSI) for a given dataset.
        :param df: pandas DataFrame with a 'Close' column containing closing prices.
        :param window: Number of periods to use for RSI calculation (default is 14).
        :return: pandas DataFrame with an additional 'RSI' column.
        """
        price_diff = df['Close'].diff(1)  # Calculate price differences
        gain = price_diff.where(price_diff > 0, 0)  # Get gains (positive differences)
        loss = -price_diff.where(price_diff < 0, 0)  # Get losses (negative differences)
        avg_gain = gain.rolling(window).mean()  # Calculate average gain
        avg_loss = loss.rolling(window).mean()  # Calculate average loss
        rs = avg_gain / avg_loss  # Calculate relative strength
        rsi = 100 - (100 / (1 + rs))  # Calculate RSI
        df['RSI'] = rsi  # Add RSI column to DataFrame
        return df

    def calc_rsi_tradingview(self, ohlc, period: int=14):

        delta = ohlc['Close'].diff()

        ohlc['up'] = delta.copy()
        ohlc['down'] = delta.copy()

        ohlc['up'] = pd.to_numeric(ohlc['up'])
        ohlc['down'] = pd.to_numeric(ohlc['down'])

        ohlc['up'][ohlc['up'] < 0] = 0
        ohlc['down'][ohlc['down'] > 0] = 0

        # This one below is not correct, but why?
        ohlc['_gain'] = ohlc['up'].ewm(com=(period - 1), min_periods=period).mean()
        ohlc['_loss'] = ohlc['down'].abs().ewm(com=(period - 1), min_periods=period).mean()

        ohlc['RS`'] = ohlc['_gain'] / ohlc['_loss']

        ohlc['rsi'] = pd.Series(100 - (100 / (1 + ohlc['RS`'])))

        self.currentvalue = round(ohlc['rsi'].iloc[-1], 8)
        ohlc.drop('up', axis=1, inplace=True)
        ohlc.drop('down', axis=1, inplace=True)
        ohlc.drop('_gain', axis=1, inplace=True)
        ohlc.drop('_loss', axis=1, inplace=True)
        ohlc.drop('RS`', axis=1, inplace=True)
        return ohlc
        #print(self.currentvalue)

        #self.exportspreadsheetfordebugging(ohlc, 'calculate_RSI_method_1', self.symbol)


