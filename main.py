import pandas as pd
import matplotlib.pyplot as plt


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

    total_trees = getTreeNumber(data)
    nan = dataF.isnull().sum()

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


# Returns tree number
def getTreeNumber(dataF):
    count = len(dataF)
    print("Total number of trees:", count, '\n')
    return count


# Returns data frame columns
def getColumns(dataF):
    return dataF.columns.values


# Prints data frame's columns
def printColumns(col):
    print(col)
    print(len(col))


#######################################################

filename = "./resources/p2-arbres-fr.csv"
data = pd.read_csv(filename, encoding='utf-8', sep=';')

# Data clean up
data = cleaningColumns(data)
data = cleaningRows(data)

# Important values
columns = getColumns(data)
row_count = getTreeNumber(data)

# Save cleaned up csv
data.to_csv('./resources/cleanedDF.csv', encoding='utf-8', sep=';')  # index = False to remove previous index column
data.reset_index(drop=True)

# Get all rows with judee as libelle_francais
index = data.index
new_val = data["libelle_francais"] == 'Arbre de Judée'
b = index[new_val]
judee_rows = b.tolist()
print("Get only rows with Arbre de Judée:", judee_rows)
print('\n', data["libelle_francais"][b[0]])

# Groupby libelle_francais
categories_grp = data.groupby('libelle_francais')
total_categories = len(categories_grp)
print("Tree categories:\n", total_categories, '\n')
print("libelle_francais grp size:\n", categories_grp.size(), '\n')

# Groupby species
species_grp = data.groupby('espece')
total_species = len(species_grp)
print("Species categories:", total_species)
print("species grp size:\n", species_grp.size(), '\n')

# Top 10 most present species in Paris
species_group = data.assign(dummy=1).groupby(['dummy', 'espece']).size(). \
    groupby(level=0).apply(lambda x: 100 * x / x.sum()).sort_values(ascending=False)
species_group.plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.2f%%')
plt.title('Species percentage in Paris')
plt.ylabel('')
plt.savefig("./resources/species_percentage.png")
plt.show()

# Tree number percentage per 'arrondissement'
arron_group = data.assign(dummy=1).groupby(['dummy', 'arrondissement']).size(). \
    groupby(level=0).apply(lambda x: 100 * x / x.sum()).sort_values(ascending=False)
arron_group.plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.2f%%')
plt.title('Tree number percentage per arrondissement')
plt.ylabel('')
plt.savefig("./resources/arrondissement_percentage.png")
plt.show()

# Tree number percentage per 'lieu'
lieu_group = data.assign(dummy=1).groupby(['dummy', 'lieu']).size(). \
    groupby(level=0).apply(lambda x: 100 * x / x.sum()).sort_values(ascending=False)
lieu_group.head(10).plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.2f%%')
plt.title('Top ten most green lieu')
plt.ylabel('')
plt.savefig("./resources/top_ten_lieu.png")
plt.show()

# Height average per arrondissement
hauteur_mean = data.groupby(['arrondissement'])['hauteur_m'].mean().reset_index().plot(x='arrondissement',
                                                                                       y='hauteur_m',
                                                                                       kind='bar', subplots=True,
                                                                                       figsize=(15, 10))
plt.title('Average height per arrondissement in meters')
plt.ylabel('')
plt.savefig("./resources/average_height_per_arrondissement.png")
plt.show()

# Circumference average per arrondissement
circum_mean = data.groupby(['arrondissement'])['circonference_cm'].mean().reset_index().plot(x='arrondissement',
                                                                                             y='circonference_cm',
                                                                                             kind='bar', subplots=True,
                                                                                             figsize=(15, 10))
plt.title('Average circumference per arrondissement in centimeters')
plt.ylabel('')
plt.savefig("./resources/average_circumference_per_arrondissement.png")
plt.show()
