import csvManager
import dfManager
import expiryDateManager
import constants
from datetime import datetime
import supertrend
import rsiManager
import os
if __name__ == '__main__':

    # initialize Trade log Dataframe
    trade_log = ['Entry_Datetime', 'Future_Traded_Price', 'Days_to_Expiry', 'Symbol', 'Entry_Price', 'Exit_Price',
                 'PnL']



    bnf_future_file_path = constants.BANKNIFTY_FUTURE_2023_PATH
    CM = csvManager.CsvManager()
    banknifty_dataframe = CM.read_csv_to_df(bnf_future_file_path)

    #***************************************************************************************************************
    #
    # get the list of all the files for given directory
    # These files are having all the FnO data
    #
    #***************************************************************************************************************
    options_data_directory = "C://Historical Data//2023"
    files = []
    for root, _, file_names in os.walk(options_data_directory):
        for file_name in file_names:
            if (bnf_future_file_path.split('//')[-1]) in file_name:
                continue
            else:
                files.append(os.path.join(root, file_name))

    #print(files)
    #***************************************************************************************************************
    #
    # Main logic will start from here, we got the list of files.
    # We will read all the files one by one and according to date will get the data from banknifty dataframe.
    #
    #
    #
    #***************************************************************************************************************
    for file_path in files:

        # get FnO Data into Dataframe
        fno_df = CM.read_csv_to_df(file_path)

        trading_date = file_path.split("\\")[-1].split("_")[-1].split(".")[0]

        # calculate Expiry Day
        EDM = expiryDateManager.ExpiryDateManager()
        expiry_date = EDM.calculate_expiry_date(trading_date)

        # expiry_date_in_option_ticker
        # this is the dat format like 05JAN23 which will be used to filter option ticker
        # for ex. BANKNIFTY05JAN2323500PE
        expiry_date_in_option_ticker = str(EDM.convert_date(expiry_date))
        print(expiry_date_in_option_ticker)

        DfManager = dfManager.DfManager()
        bnf_options_df = DfManager.filter_BnfOptions_data(fno_df, expiry_date_in_option_ticker)
        bnf_options_five_min_df = DfManager.get_custom_min_ohlc(bnf_options_df, '5Min')

        trading_date_temp = datetime.strptime(trading_date, "%d%m%Y")
        trading_date_dd_mm_yyyy = str(trading_date_temp.strftime("%d-%m-%Y"))

        #*****************************************************************************************************
        # get banknifty inraday daya from dataframe which has complete year ohlc data
        #*****************************************************************************************************
        banknifty_itraday_df = banknifty_dataframe[(banknifty_dataframe['Date'] == trading_date_dd_mm_yyyy)]


        break





