import os

import pandas as pd

import csvManager
import dfManager
import expiryDateManager
import constants
import supertrend
import rsiManager


def get_files_from_directory(directory):
    """
    Get a list of all files in a directory.
    :param directory: Path to the directory.
    :return: List of file names.
    """
    files = []
    for root, _, file_names in os.walk(directory):
        for file_name in file_names:
            files.append(os.path.join(root, file_name))
    return files

# Specify the directory path
directory_path = "C://Historical Data//2023"

# Get the list of files in the directory
file_list = get_files_from_directory(directory_path)
complete_banknifty_futures_data = pd.DataFrame(columns=['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Time'])
index = 0

# Print the list of files
for file_name in file_list:
    print(file_name)
    CM = csvManager.CsvManager()
    data_as_df = CM.read_csv_to_df(file_name)

    DfManager = dfManager.DfManager()
    banknifty_future_df = DfManager.filter_Banknifty_future(data_as_df)

    banknifty_five_min_df = DfManager.get_custom_min_ohlc(banknifty_future_df, '5Min')
    # add supertrend to Banknifty Future Dataframe


    complete_banknifty_futures_data = pd.concat([complete_banknifty_futures_data, banknifty_five_min_df], ignore_index=True)
    index = index + 1


#sort data frame by date and time
#complete_banknifty_futures_data = complete_banknifty_futures_data.sort_values(['Date','Time'])

ST = supertrend.StManager()
st_df = ST.calculate_tradingView_ST(complete_banknifty_futures_data, 10, 2)
banknifty_five_min_df_with_st_2023 = complete_banknifty_futures_data.join(st_df)

# add RSI to Banknifty Future Dataframe
RSI = rsiManager.RSIManager()
banknifty_five_min_df_with_st_rsi_2023 = RSI.calc_rsi_tradingview(banknifty_five_min_df_with_st_2023)

banknifty_five_min_df_with_st_rsi_2023.to_csv('C://Historical Data//2023//BANKNIFTY_2023_ST_RSI.csv', index=False)

