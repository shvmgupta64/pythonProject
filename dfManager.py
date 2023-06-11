import pandas as pd

#this method is to read the csv into df
#@input will be file_path
class DfManager:

    def __init__(self):
        pass

    def filter_Banknifty_future(self, df):
        filtered_df = df[df['Ticker'] == "BANKNIFTY-I"]
        return filtered_df

    def filter_BnfOptions_data(self, df, expiryDate):
        filtered_options_df = "temp"
        return filtered_options_df
        