import pandas as pd
import csvManager
import expiryDateManager
'''
file_path  = "C://Historical Data//2023//banknifty_2023_st_RSI.csv"
df = pd.read_csv(file_path)
df = df.sort_values(['Date','Time'])
df.to_csv('C://Historical Data//2023//banknifty_2023_st_RSI_sorted.csv', index=False)
'''
trading_date = "16022023"
EDM = expiryDateManager.ExpiryDateManager()
expiry_date = EDM.calculate_expiry_date(trading_date)
print(expiry_date)
