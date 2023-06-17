import csvManager
import pandas as pd
import supertrend
import rsiManager

filePath = "C://Historical Data//2023//complete_banknifty_futures_data_2023.csv"
CM = csvManager.CsvManager()
data_as_df = CM.read_csv_to_df(filePath)
pd.options.mode.chained_assignment = None


ST = supertrend.StManager()
banknifty_five_min_df_with_st_2023 = ST.calculate_supertrend(data_as_df, 10, 2)

# add RSI to Banknifty Future Dataframe
RSI = rsiManager.RSIManager()
banknifty_five_min_df_with_st_rsi_2023 = RSI.calc_rsi_tradingview(banknifty_five_min_df_with_st_2023)


CM.create_csf_from_df(banknifty_five_min_df_with_st_rsi_2023)
