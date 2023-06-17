import pandas as pd
import csvManager
import dfManager
import expiryDateManager
import constants
from datetime import datetime
import os

if __name__ == '__main__':

    # initialize Trade log Dataframe
    trade_log = pd.DataFrame(columns=['Symbol', 'Date', 'Buy-Sell', 'Future_Traded_Price', 'Entry_Datetime', 'Entry_Price', 'Exit_Datetime',
                 'Exit_Price', 'PnL'])
    trade_index = 0

    bnf_future_file_path = constants.BANKNIFTY_FUTURE_2023_PATH
    CM = csvManager.CsvManager()
    banknifty_dataframe = CM.read_csv_to_df(bnf_future_file_path)

    #***************************************************************************************************************
    #
    # get the list of all the files for given directory
    # These files are having all the FnO data
    #
    #***************************************************************************************************************
    options_data_directory = "C://temp_testing"
    files = []
    for root, _, file_names in os.walk(options_data_directory):
        for file_name in file_names:
            if (bnf_future_file_path.split('//')[-1]) in file_name:
                continue
            else:
                files.append(os.path.join(root, file_name))


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
        print(file_path)
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
                #print(ticker_strike_price)
                intraday_options_tickers.append(ticker)

        bnf_options_five_min_df = pd.DataFrame(
            columns=['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Time'])

        for ticker in intraday_options_tickers:
            #print(ticker)
            option_unique_ticker_df = bnf_options_df[bnf_options_df['Ticker'] == ticker]
            unique_ticker_five_min_ohlc = DfManager.get_custom_min_ohlc(option_unique_ticker_df, '5Min')
            bnf_options_five_min_df = pd.concat([bnf_options_five_min_df,unique_ticker_five_min_ohlc])


        current_trade_straddle = False
        current_trade_synFut = False
        max_rsi = 0
        min_rsi = 0
        temp_max_rsi = 0
        temp_min_rsi = 0
        ce_found = False
        pe_found = False
        intraday_trade_counter = 0
        synth_fut_trigger_price = 0
        synth_fut_buy_sell = ""
        ce_buy_sell = ""
        pe_buy_sell = ""
        pnl = 0

        for index, row in banknifty_itraday_df.iterrows():

            if current_trade_synFut:
                if synth_fut_buy_sell == "Buy":

                    if row['Close'] < banknifty_itraday_df.loc[index - 1, 'Final Lowerband'] and banknifty_itraday_df.loc[index - 1, 'Final Lowerband'] is not None:
                        # synthetic SL hit
                        # check pnl
                        ce_found = False
                        pe_found = False

                        for index, bnf_options in bnf_options_five_min_df.iterrows():
                            if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == row['Time']:
                                ce_pnl = bnf_options['Close'] - ce_buy_price
                                ce_sell_price = bnf_options['Close']
                                ce_found = True

                            if bnf_options['Ticker'] == pe_straddle_symbol and bnf_options['Time'] == row['Time']:
                                ce_pnl = pe_sell_price - bnf_options['Close']
                                pe_buy_price = bnf_options['Close']
                                pe_found = True

                            if ce_found and pe_found:
                                break

                        if intraday_trade_counter > 1:
                            pnl = ce_pnl + pe_pnl + booked_pnl
                        else:
                            pnl = ce_pnl + pe_pnl

                        if pnl < constants.INTRADAY_SL_LIMIT or row['Time'] == constants.TRADE_END_TIME:
                            # close all trades
                            ce_exit_time = row['Time']
                            pe_exit_time = row['Time']

                            intraday_log = [ce_straddle_symbol, trading_date_dd_mm_yyyy, ce_buy_sell,
                                        fut_traded_price,
                                        ce_entry_time, ce_buy_price, ce_exit_time,
                                        ce_sell_price, ce_pnl]

                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1

                            intraday_log = [pe_straddle_symbol, trading_date_dd_mm_yyyy, pe_buy_sell,
                                            fut_traded_price,
                                            pe_entry_time, pe_sell_price, pe_exit_time,
                                            pe_buy_price, pe_pnl]

                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1
                            booked_pnl = pnl
                        else:
                            # convert synthetic to straddle
                            # close CE buy and sell it again
                            current_trade_straddle = True
                            current_trade_synFut = False
                            max_rsi = 0
                            min_rsi = 0
                            temp_max_rsi = 0
                            temp_min_rsi = 0

                            ce_exit_time = row['Time']
                            intraday_log = [ce_straddle_symbol, trading_date_dd_mm_yyyy, ce_buy_sell,
                                            fut_traded_price,
                                            ce_entry_time, ce_buy_price, ce_exit_time,
                                            ce_sell_price, ce_pnl]
                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1
                            ce_buy_sell = "Sell"
                            ce_entry_time = row['Time']

                if synth_fut_buy_sell == "Sell":
                    #print(row['Close'])
                    #print(row['Final Lowerband'])
                    if row['Close'] > banknifty_itraday_df.loc[index - 1, 'Final Upperband'] and banknifty_itraday_df.loc[index - 1, 'Final Upperband'] is not None :

                        # synthetic SL hit
                        # check pnl
                        ce_found = False
                        pe_found = False

                        for index, bnf_options in bnf_options_five_min_df.iterrows():
                            if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == row['Time']:
                                ce_pnl = ce_sell_price - bnf_options['Close']
                                ce_buy_price = bnf_options['Close']
                                ce_found = True

                            if bnf_options['Ticker'] == pe_straddle_symbol and bnf_options['Time'] == row['Time']:
                                pe_pnl = bnf_options['Close'] - pe_buy_price
                                pe_sell_price = bnf_options['Close']
                                pe_found = True

                            if ce_found and pe_found:
                                break

                        if intraday_trade_counter > 1:
                            pnl = ce_pnl + pe_pnl + booked_pnl
                        else:
                            pnl = ce_pnl + pe_pnl

                        if pnl < constants.INTRADAY_SL_LIMIT or row['Time'] == constants.TRADE_END_TIME:
                            # close all trades
                            ce_exit_time = row['Time']
                            pe_exit_time = row['Time']
                            synth_fut_trigger_price = 0

                            intraday_log = [ce_straddle_symbol, trading_date_dd_mm_yyyy, ce_buy_sell,
                                            fut_traded_price,
                                            ce_entry_time, ce_sell_price, ce_exit_time,
                                            ce_buy_price, ce_pnl]

                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1

                            intraday_log = [pe_straddle_symbol, trading_date_dd_mm_yyyy, pe_buy_sell,
                                            fut_traded_price,
                                            pe_entry_time, pe_buy_price, pe_exit_time,
                                            pe_sell_price, pe_pnl]

                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1
                            booked_pnl = pnl
                        else:
                            # convert synthetic to straddle
                            # close PE buy and sell it again
                            print("Convert Synthetic Future to Straddle")
                            print(row['Time'])
                            current_trade_straddle = True
                            current_trade_synFut = False
                            synth_fut_trigger_price = 0
                            max_rsi = 0
                            min_rsi = 0
                            temp_max_rsi = 0
                            temp_min_rsi = 0


                            pe_exit_time = row['Time']
                            intraday_log = [pe_straddle_symbol, trading_date_dd_mm_yyyy, pe_buy_sell,
                                            fut_traded_price,
                                            pe_entry_time, pe_buy_price, pe_exit_time,
                                            pe_sell_price, pe_pnl]
                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1

                            pe_buy_sell = "Sell"
                            pe_entry_time = row['Time']

            if current_trade_straddle:

                ce_found = False
                pe_found = False
                #calculate pnl for current trade
                for index, bnf_options in bnf_options_five_min_df.iterrows():
                    if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == row['Time']:
                        ce_pnl = ce_sell_price - bnf_options['Close']
                        ce_buy_price = bnf_options['Close']
                        ce_found = True

                    if bnf_options['Ticker'] == pe_straddle_symbol and bnf_options['Time'] == row['Time']:
                        pe_pnl = pe_sell_price - bnf_options['Close']
                        pe_buy_price = bnf_options['Close']
                        pe_found = True
                    if ce_found and pe_found:
                        break

                if intraday_trade_counter > 1:
                    pnl = ce_pnl + pe_pnl + booked_pnl
                else:
                    pnl = ce_pnl + pe_pnl


                if pnl < constants.INTRADAY_SL_LIMIT or row['Time'] == constants.TRADE_END_TIME:
                    #close all the straddle
                    ce_exit_time = row['Time']
                    pe_exit_time = row['Time']

                    intraday_log = [ce_straddle_symbol, trading_date_dd_mm_yyyy, ce_buy_sell,
                                    fut_traded_price,
                                    ce_entry_time, ce_sell_price, ce_exit_time,
                                    ce_buy_price, ce_pnl]

                    trade_log.loc[trade_index] = intraday_log
                    trade_index = trade_index + 1

                    intraday_log = [pe_straddle_symbol, trading_date_dd_mm_yyyy, pe_buy_sell,
                                    fut_traded_price,
                                    pe_entry_time, pe_sell_price, pe_exit_time,
                                    pe_buy_price, pe_pnl]

                    trade_log.loc[trade_index] = intraday_log
                    trade_index = trade_index + 1
                    booked_pnl = pnl
                else:
                    ce_buy_price = 0
                    pe_buy_price = 0

            if row['Time'] == constants.FIRST_STRADDLE_TIME:
                straddle_strike_price = str(constants.BANKNIFTY_BASE*round(row['Open']/constants.BANKNIFTY_BASE))
                ce_straddle_symbol = 'BANKNIFTY' + expiry_date_in_option_ticker + straddle_strike_price + 'CE.NFO'
                pe_straddle_symbol = 'BANKNIFTY' + expiry_date_in_option_ticker + straddle_strike_price + 'PE.NFO'
                ce_entry_set = False
                pe_entry_set = False
                ce_buy_price = 0
                pe_sell_price = 0
                ce_sell_price = 0
                pe_buy_price = 0

                for index, bnf_options in bnf_options_five_min_df.iterrows():
                    if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == constants.FIRST_STRADDLE_TIME:
                        ce_sell_price = bnf_options['Open']
                        ce_entry_time = bnf_options['Time']
                        ce_buy_sell = "Sell"
                        ce_found = True

                    if bnf_options['Ticker'] == pe_straddle_symbol and bnf_options['Time'] == constants.FIRST_STRADDLE_TIME:
                        pe_sell_price = bnf_options['Open']
                        pe_entry_time = bnf_options['Time']
                        pe_buy_sell = "Sell"
                        pe_found = True

                    if ce_found == True and pe_found == True:
                        fut_traded_price = row['Close']
                        break

                current_trade_straddle = True
                print("***********************----Trade starts on "+trading_date+"----***********************")
                print("***********************----Straddle Entry at 9:20----*********************")
                print(ce_straddle_symbol+" sold at "+str(ce_sell_price))
                print(pe_straddle_symbol + " sold at " + str(pe_sell_price))
                print("+++++++++++++++++++++++----Straddle Entry at 9:20----+++++++++++++++++++++")

            if current_trade_straddle == True:

                if row['rsi'] is not None and row['rsi'] > constants.RSI_BAND_HIGH and (
                        index == 0 or row['rsi'] > banknifty_itraday_df.loc[index - 1, 'rsi']):
                    if max_rsi == 0:
                        temp_max_rsi = row['rsi']
                        temp_max_price = row['High']
                        temp_min_rsi = 0
                        min_rsi = 0

                if index < len(banknifty_itraday_df) - 1 and banknifty_itraday_df.loc[index + 1, 'rsi'] is not None and \
                        banknifty_itraday_df.loc[index + 1, 'rsi'] < row['rsi']:
                    if temp_max_rsi != 0:
                        max_rsi = temp_max_rsi
                        synth_fut_trigger_price = temp_max_price
                        synth_fut_buy_sell = 'Buy'


                if row['rsi'] is not None and row['rsi'] < constants.RSI_BAND_LOW and (
                        index == 0 or row['rsi'] < banknifty_itraday_df.loc[index - 1, 'rsi']):
                    if min_rsi == 0:
                        temp_min_rsi = row['rsi']
                        temp_min_price = row['Low']
                        temp_max_rsi = 0
                        max_rsi = 0


                if index < len(banknifty_itraday_df) - 1 and banknifty_itraday_df.loc[index + 1, 'rsi'] is not None and \
                        banknifty_itraday_df.loc[index + 1, 'rsi'] > row['rsi']:
                    if temp_min_rsi != 0:
                        min_rsi = temp_min_rsi
                        synth_fut_trigger_price = temp_min_price
                        synth_fut_buy_sell = 'Sell'

                if row['Close'] > synth_fut_trigger_price and  current_trade_straddle and synth_fut_trigger_price != 0\
                        and synth_fut_buy_sell == "Buy":
                        current_trade_synFut = True
                        current_trade_straddle = False
                        fut_traded_price = row['Close']

                        #Close Straddle
                        for index, bnf_options in bnf_options_five_min_df.iterrows():

                            if bnf_options['Ticker'] == ce_straddle_symbol and bnf_options['Time'] == row['Time']:
                                ce_buy_price = bnf_options['Close']
                                ce_exit_time = bnf_options['Time']

                                ce_pnl = ce_sell_price - ce_buy_price

                                if intraday_trade_counter > 0:
                                    booked_pnl = ce_pnl + booked_pnl
                                else:
                                    booked_pnl = ce_pnl


                                intraday_trade_counter = intraday_trade_counter + 1
                                intraday_log = [ce_straddle_symbol, trading_date_dd_mm_yyyy, ce_buy_sell,
                                                fut_traded_price,
                                                ce_entry_time, ce_sell_price, ce_exit_time,
                                                ce_buy_price, ce_pnl]

                                trade_log.loc[trade_index] = intraday_log
                                trade_index = trade_index + 1

                                # trigger synthetic future
                                ce_buy_sell = "Buy"
                                ce_buy_price = bnf_options['Close']
                                ce_entry_time = bnf_options['Time']
                                break

                if row['Close'] < synth_fut_trigger_price and current_trade_straddle and synth_fut_trigger_price != 0 \
                        and synth_fut_buy_sell == "Sell":

                    current_trade_synFut = True
                    current_trade_straddle = False
                    fut_traded_price = row['Close']

                    # Close Straddle
                    for index, bnf_options in bnf_options_five_min_df.iterrows():

                        if bnf_options['Ticker'] == pe_straddle_symbol and bnf_options['Time'] == row['Time']:
                            pe_buy_price = bnf_options['Close']
                            pe_exit_time = bnf_options['Time']

                            pe_pnl = pe_sell_price - pe_buy_price

                            if intraday_trade_counter > 0:
                                booked_pnl = pe_pnl + booked_pnl
                            else:
                                booked_pnl = pe_pnl

                            intraday_trade_counter = intraday_trade_counter + 1
                            intraday_log = [pe_straddle_symbol, trading_date_dd_mm_yyyy, pe_buy_sell,
                                            fut_traded_price,
                                            pe_entry_time, pe_sell_price, pe_exit_time,
                                            pe_buy_price, pe_pnl]

                            trade_log.loc[trade_index] = intraday_log
                            trade_index = trade_index + 1

                            # trigger synthetic future
                            pe_buy_sell = "Buy"
                            pe_buy_price = bnf_options['Close']
                            pe_entry_time = bnf_options['Time']
                            break


        #break

trade_log.to_csv('C://Historical Data//trade_log.csv')
print(trade_log)




