import csvManager
import dfManager

if __name__ == '__main__':
    file_path = "C://Historical Data//2020//01//GFDLNFO_01012020.csv"
    CM = csvManager.CsvManager()
    df = CM.read_csv_to_df(file_path)

    DfManager = dfManager.DfManager()
    bankniftyFutureDf = DfManager.filter_Banknifty_future(df)
    print(bankniftyFutureDf)
