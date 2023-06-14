import pandas as pd
import csvManager
import dfManager
import expiryDateManager
import constants
from datetime import datetime
import os

if __name__ == '__main__':

    # initialize Trade log Dataframe
    trade_log = ['Symbol', 'Date', 'Buy-Sell', 'Future_Traded_Price', 'Entry_Datetime', 'Entry_Price', 'Exit_Datetime',
                 'Exit_Price', 'PnL']
    trade_log_count = 0

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
    trade_log_index = 0
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

        trading_date_temp = datetime.strptime(trading_date, "%d%m%Y")
        trading_date_dd_mm_yyyy = str(trading_date_temp.strftime("%d-%m-%Y"))

        # *****************************************************************************************************
        # get banknifty inraday daya from dataframe which has complete year ohlc data
        # *****************************************************************************************************

        banknifty_itraday_df = banknifty_dataframe[(banknifty_dataframe['Date'] == trading_date_dd_mm_yyyy)]
        banknifty_intraday_high = banknifty_itraday_df['High'].max()
        banknifty_intraday_low = banknifty_itraday_df['Low'].min()

        DfManager = dfManager.DfManager()
        bnf_options_df = DfManager.filter_BnfOptions_data(fno_df, expiry_date_in_option_ticker)
        all_options_tickers = bnf_options_df['Ticker'].unique()
        intraday_options_tickers = []

        for ticker in all_options_tickers:
            ticker_strike_price = int(ticker[16:21])
            if ticker_strike_price < banknifty_intraday_high and ticker_strike_price > banknifty_intraday_low:
                intraday_options_tickers.append(ticker)

        bnf_options_five_min_df = pd.DataFrame(
            columns=['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Time'])

        for ticker in intraday_options_tickers:
            option_unique_ticker_df = bnf_options_df[bnf_options_df['Ticker'] == ticker]
            unique_ticker_five_min_ohlc = DfManager.get_custom_min_ohlc(option_unique_ticker_df, '5Min')
            bnf_options_five_min_df = pd.concat([bnf_options_five_min_df,unique_ticker_five_min_ohlc])


        current_trade_straddle = False
        current_trade_synFut = False
        max_rsi = 0
        temp_rsi = 0
        close_straddle = False
        intraday_trade_counter = 0


        for index, row in banknifty_itraday_df.iterrows():

            if row['Time'] == constants.FIRST_STRADDLE_TIME:
                buy_sell = 'Sell'
                straddle_strike_price = str(constants.BANKNIFTY_BASE*round(row['Open']/constants.BANKNIFTY_BASE))
                ce_straddle_symbol = 'BANKNIFTY' + expiry_date_in_option_ticker + straddle_strike_price + 'CE.NFO'
                pe_straddle_symbol = 'BANKNIFTY' + expiry_date_in_option_ticker + straddle_strike_price + 'PE.NFO'
                ce_entry_set = False
                pe_entry_set = False
                ce_straddle_entry_price = 0
                pe_straddle_entry_price = 0

                for index, bnf_options in bnf_options_five_min_df.iterrows():
                    if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == constants.FIRST_STRADDLE_TIME:
                        ce_straddle_entry_price = bnf_options['Open']
                        ce_straddle_entry_time = bnf_options['Time']
                        ce_entry_set = True

                    if bnf_options['Ticker'] == pe_straddle_symbol and bnf_options['Time'] == constants.FIRST_STRADDLE_TIME:
                        pe_straddle_entry_price = bnf_options['Open']
                        pe_straddle_entry_time = bnf_options['Time']
                        pe_entry_set = True

                    if ce_entry_set == True and pe_entry_set == True:
                        fut_traded_price = row['Close']
                        break

                current_trade_straddle = True
                print("***********************----Trade starts on "+trading_date+"----***********************")
                print("***********************----Straddle Entry at 9:20----*********************")
                print(ce_straddle_symbol+" sold at "+str(ce_straddle_entry_price))
                print(pe_straddle_symbol + " sold at " + str(pe_straddle_entry_price))
                print("+++++++++++++++++++++++----Straddle Entry at 9:20----+++++++++++++++++++++")

            if row['rsi'] is not None and row['rsi'] > constants.RSI_BAND_HIGH and (
                    index == 0 or row['rsi'] > banknifty_itraday_df.loc[index - 1, 'rsi']):
                if max_rsi == 0:
                    temp_rsi = row['rsi']
                    temp_max_price = row['Close']

            if index < len(banknifty_itraday_df) - 1 and banknifty_itraday_df.loc[index + 1, 'rsi'] is not None and \
                    banknifty_itraday_df.loc[index + 1, 'rsi'] < row['rsi']:
                if temp_rsi != 0:
                    max_rsi = temp_rsi
                    synth_fut_trigger_price = temp_max_price
                    synth_fut_buy_sell = 'Buy'
                    close_straddle = True

            if close_straddle:
                if row['Close'] > synth_fut_trigger_price and  current_trade_straddle and synth_fut_buy_sell == 'Buy':
                    current_trade_synFut = True

                    for index, bnf_options in bnf_options_five_min_df.iterrows():
                        if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == row['Time']:
                            ce_straddle_exit_price = bnf_options['Close']
                            ce_straddle_exit_time = bnf_options['Time']
                            break

                    if buy_sell == 'Sell':
                        ce_pnl = ce_straddle_entry_price - ce_straddle_exit_price

                        intraday_log = [ce_straddle_symbol,trading_date_dd_mm_yyyy, buy_sell, fut_traded_price,
                                        ce_straddle_entry_time, ce_straddle_entry_price, ce_straddle_exit_time,
                                        ce_straddle_exit_price, ce_pnl]




















        break





