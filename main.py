import csvManager
import dfManager
import expiryDateManager
import constants
import supertrend
import rsiManager

if __name__ == '__main__':

    file_path = constants.FILE_PATH
    CM = csvManager.CsvManager()
    data_as_df = CM.read_csv_to_df(file_path)

    #calculate Trading Date
    trading_date = file_path.split("//")[-1].split("_")[-1].split(".")[0]

    #calculate Expiry Day
    EDM = expiryDateManager.ExpiryDateManager()
    expiry_date = EDM.calculate_expiry_date(trading_date)
    expiry_date_in_option_ticker = str(EDM.convert_date(expiry_date))

    #create banknifty future dataframe
    #create banknifty options dataframe
    DfManager = dfManager.DfManager()
    banknifty_future_df = DfManager.filter_Banknifty_future(data_as_df)
    options_df = DfManager.filter_BnfOptions_data(data_as_df, expiry_date_in_option_ticker)


    # call get_custom_min_ohlc method to convert 1 min timeframe DF to 5 min timeframe DF
    banknifty_five_min_df = DfManager.get_custom_min_ohlc(banknifty_future_df,'5Min')
    bnf_options_five_min_df = DfManager.get_custom_min_ohlc(options_df,'5Min')


    #add supertrend to Banknifty Future Dataframe
    ST = supertrend.StManager()
    banknifty_five_min_df_with_st = ST.calculate_supertrend(banknifty_five_min_df, 7, 2)

    #add RSI to Banknifty Future Dataframe
    RSI = rsiManager.RSIManager()
    banknifty_five_min_df_with_st_rsi = RSI.calculate_rsi(banknifty_five_min_df_with_st)
    print(banknifty_five_min_df_with_st_rsi)
    CM.create_csf_from_df(banknifty_five_min_df_with_st_rsi)









