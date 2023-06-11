import pandas as pd
import csv

#this method is to read the csv into df
#@input will be file_path
class CsvManager:

    def __init__(self):
        pass

    def read_csv_to_df(self,file_path):
        df = pd.read_csv(file_path)
        return df

    def create_csf_from_df(self, df):
        df.to_csv("C://Users//Lenovo//Desktop//df_csv.csv")