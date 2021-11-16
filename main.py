import pandas as pd


# Returns data frame columns
def getColumns(dataF):
    return dataF.columns.values


# Prints data frame's columns
def printColumns(col):
    print(col)
    print(len(col))


# Removing unwanted columns from data frame
def cleaningColumns(dataF):
    dataF.drop('type_emplacement', axis=1, inplace=True)
    dataF.drop('domanialite', axis=1, inplace=True)
    dataF.drop('complement_addresse', axis=1, inplace=True)
    dataF.drop('numero', axis=1, inplace=True)
    dataF.drop('id_emplacement', axis=1, inplace=True)
    dataF.drop('variete', axis=1, inplace=True)
    dataF.drop('geo_point_2d_a', axis=1, inplace=True)
    dataF.drop('geo_point_2d_b', axis=1, inplace=True)
    dataF.drop('stade_developpement', axis=1, inplace=True)
    dataF.drop('remarquable', axis=1, inplace=True)
    return dataF


# Removing unwanted lines from data frame
def cleaningRows(dataF):
    dataF.drop(dataF.index[(dataF["circonference_cm"] <= 0)], axis=0, inplace=True)
    dataF.drop(dataF.index[(dataF["hauteur_m"] <= 0)], axis=0, inplace=True)
    # biggest circumference paris tree 4,70 m -> 470 cm
    dataF.drop(dataF.index[(dataF["circonference_cm"] > 470)], axis=0, inplace=True)
    # tallest paris tree 35 m -> 3500 cm
    dataF.drop(dataF.index[(dataF["hauteur_m"] > 40)], axis=0, inplace=True)
    return dataF


filename = "./resources/p2-arbres-fr.csv"
data = pd.read_csv(filename, encoding='utf-8', sep=';')

columns = getColumns(data)
print("Before cleaning up")
printColumns(columns)

data = cleaningColumns(data)
columns = getColumns(data)
print("After cleaning up")
printColumns(columns)

data = cleaningRows(data)

data.to_csv('./resources/cleanedDF.csv', encoding='utf-8', sep=';')

chene = data.loc[data['id'] == '99874']
print(data['libelle_francais'].values[16])

"""
UTF 8 problem
Ãª = ê
Ã = à
Ã« = è
Ã» = û MÃ»rier
Ã¨ = è Faux-cyprÃ¨s
Ã© = é AubÃ©pine
"""
