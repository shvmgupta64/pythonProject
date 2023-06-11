#***************************************************************************
#
#This class is created to manager dataframes.
#all the operations related to data frames, will be conducted in this class.
#
#
#**************************************************************************

import pandas as pd
import datetime

class StManager:

    def __init__(self):
        pass

    # Calculate Supertrend indicator
    def calculate_supertrend(self, df, period=10, multiplier=2):
        """
        Function to calculate Supertrend indicator given a DataFrame
        """
        df['ATR'] = 0.00
        df['Supertrend'] = 0.00

        hl_range = df['High'] - df['Low']
        hc_range = abs(df['High'] - df['Close'].shift())
        lc_range = abs(df['Low'] - df['Close'].shift())

        df['TR'] = pd.concat([hl_range, hc_range, lc_range], axis=1).max(axis=1)
        df['ATR'] = df['TR'].rolling(period).mean()
        df['Upperband'] = df['High'] - (multiplier * df['ATR'])
        df['Lowerband'] = df['Low'] + (multiplier * df['ATR'])

        for current in range(1, len(df.index)):
            previous = current - 1

            if df['Close'][current] > df['Supertrend'][previous]:
                df['Supertrend'][current] = df['Upperband'][current]
            else:
                df['Supertrend'][current] = df['Lowerband'][current]

            if df['Close'][current] < df['Lowerband'][current]:
                df['Supertrend'][current] = df['Lowerband'][current]

            if df['Close'][current] > df['Upperband'][current]:
                df['Supertrend'][current] = df['Upperband'][current]

        df.drop('Upperband', axis=1, inplace=True)
        df.drop('Lowerband', axis=1, inplace=True)
        df.drop('TR', axis=1, inplace=True)
        return df

