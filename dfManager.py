#***************************************************************************
#
#This class is created to manager dataframes.
#all the operations related to data frames, will be conducted in this class.
#
#
#**************************************************************************

import pandas as pd
import datetime

class DfManager:

    def __init__(self):
        pass

    def filter_Banknifty_future(self, df):
        filtered_df = df[df['Ticker'].str.startswith("BANKNIFTY-I.NFO")]
        #filtered_df = df[df['Ticker'] == "BANKNIFTY-I"]
        return self.sort_dataframe(filtered_df)

    def filter_BnfOptions_data(self, df, expiry_date):
        option_symbol_format = "BANKNIFTY"+expiry_date
        filtered_options_df = df[df['Ticker'].str.startswith(option_symbol_format)]
        return self.sort_dataframe(filtered_options_df)

    def sort_dataframe(self, df):
        pd.options.mode.chained_assignment = None
        df['Time'] = df['Time'].apply(lambda x: datetime.datetime.strptime(x, '%H:%M:%S').time())
        #df.loc[:, 'Time'] = df['Time']
        sorted_df = df.sort_values(['Time'])
        return sorted_df

    #****************************************************************************************************
    #
    # Convert Banknifty 1 min Dataframe to 5 Min DF
    # input will be
    # dataframe -- 1 min Data frame
    # Time interval and format should be '5Min' or '3Min' or '10Min'
    #
    # ***************************************************************************************************
    def get_custom_min_ohlc(self, df, min='5Min'):
        df['Timestamp'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
        df.set_index('Timestamp', inplace=True)
        def custom_resampler(df):
            return pd.Series({
                'Ticker': df['Ticker'].iloc[0],
                'Date': df['Date'].iloc[0],
                'Open': df['Open'].iloc[0],
                'High': df['High'].max(),
                'Low': df['Low'].min(),
                'Close': df['Close'].iloc[-1]
            })
        five_min_df = df.groupby(pd.Grouper(freq=min)).apply(custom_resampler)
        five_min_df.dropna(inplace=True)
        five_min_df.reset_index(inplace=True)
        five_min_df['Time'] = five_min_df['Timestamp'].dt.strftime('%H:%M:%S')
        five_min_df.drop('Timestamp', axis=1, inplace=True)
        return five_min_df

