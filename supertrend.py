#***************************************************************************
#
#This class is created to manager dataframes.
#all the operations related to data frames, will be conducted in this class.
#
#
#**************************************************************************

import pandas as pd
import numpy as np
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

        #df.drop('Upperband', axis=1, inplace=True)
        #df.drop('Lowerband', axis=1, inplace=True)
        df.drop('TR', axis=1, inplace=True)
        return df

    def calculate_tradingView_ST(self, df, atr_period=10, multiplier=2):
        high = df['High']
        low = df['Low']
        close = df['Close']

        # calculate ATR
        price_diffs = [high - low,
                       high - close.shift(),
                       close.shift() - low]
        true_range = pd.concat(price_diffs, axis=1)
        true_range = true_range.abs().max(axis=1)
        # default ATR calculation in supertrend indicator
        atr = true_range.ewm(alpha=1 / atr_period, min_periods=atr_period).mean()
        # df['atr'] = df['tr'].rolling(atr_period).mean()

        # HL2 is simply the average of high and low prices
        hl2 = (high + low) / 2
        # upperband and lowerband calculation
        # notice that final bands are set to be equal to the respective bands
        final_upperband = upperband = hl2 + (multiplier * atr)
        final_lowerband = lowerband = hl2 - (multiplier * atr)

        # initialize Supertrend column to True
        supertrend = [True] * len(df)

        for i in range(1, len(df.index)):
            curr, prev = i, i - 1

            # if current close price crosses above upperband
            if close[curr] > final_upperband[prev]:
                supertrend[curr] = True
            # if current close price crosses below lowerband
            elif close[curr] < final_lowerband[prev]:
                supertrend[curr] = False
            # else, the trend continues
            else:
                supertrend[curr] = supertrend[prev]

                # adjustment to the final bands
                if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                    final_lowerband[curr] = final_lowerband[prev]
                if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                    final_upperband[curr] = final_upperband[prev]

            # to remove bands according to the trend direction
            if supertrend[curr] == True:
                final_upperband[curr] = np.nan
            else:
                final_lowerband[curr] = np.nan

        return pd.DataFrame({
            'Supertrend': supertrend,
            'Final Lowerband': final_lowerband,
            'Final Upperband': final_upperband
        }, index=df.index)


