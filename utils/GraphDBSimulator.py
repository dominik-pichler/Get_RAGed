import pandas as pd
class GraphDBSimulator:
    def __init__(self):
        self.csv_path = 'data/FBU_Testfaelle.csv'
        self.df_FBU_Testfaelle = pd.read_csv(self.csv_path)

    def fetch_n_rows_from_DB(self,number_of_rows:int) -> pd.DataFrame:
        #TODO: Implement me when needed
        pass