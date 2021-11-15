import pandas as pd

data = pd.read_csv("./resources/p2-arbres-fr.csv")
data.sort_values(["circonference"], axis=0, ascending=[False], inplace=True)
