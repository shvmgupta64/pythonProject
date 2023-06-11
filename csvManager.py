import pandas as pd

#this method is to read the csv into df
#@input will be file_path
class CsvManager:

    def __init__(self):
        pass

    def read_csv_to_df(self,file_path):
        df = pd.read_csv(file_path)
        return df
