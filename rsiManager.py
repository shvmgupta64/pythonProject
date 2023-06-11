#***************************************************************************
#
#This class is created to manager dataframes.
#all the operations related to data frames, will be conducted in this class.
#
#
#**************************************************************************

import pandas as pd
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
