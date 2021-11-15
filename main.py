import pandas as pd
filename = "./resources/p2-arbres-fr.csv"
data = pd.read_csv(filename, sep=';')
for row in data.columns:
    print(row + '\n')
columns = data.columns.values
print(columns)
print(len(columns))
