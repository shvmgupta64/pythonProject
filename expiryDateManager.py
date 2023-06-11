import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta, TH
import constants



#this method is to read the csv into df
#@input will be file_path
class ExpiryDateManager:

    def __init__(self):
        pass

    def calculate_expiry_date(self,trading_date):
        trading_year = trading_date[-4:]
        holidays_df = pd.read_csv(constants.HOLIDAY_PATH)

        #holidays list for year
        holiday_list_of_trading_year = holidays_df[trading_year]
        trading_date_in_dateFormat = datetime.datetime.strptime(trading_date,'%d%m%Y')
        expiry_day = trading_date_in_dateFormat.date() + relativedelta(weekday=TH(+1))

        for holiday in holiday_list_of_trading_year:
            holiday_dFormat = datetime.datetime.strptime(holiday,'%d-%m-%Y').date()

            if holiday_dFormat == expiry_day:
                return expiry_day - datetime.timedelta(days=1)

        return expiry_day

    #
    #convert date format from dd-mm-yyyy to ddmmmyy
    #for example: 02-03-2020 to 02MAR20
    def convert_date(self, date):
        # Convert the string to a datetime object
        return date.strftime("%d%b%y").upper()


