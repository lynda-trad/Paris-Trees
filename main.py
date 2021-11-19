# # Library used

import folium as folium
import pandas as pd
import matplotlib.pyplot as plt
import missingno as msno


# # Useful functions

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


# # Retrieving data from the csv file

filename = "./resources/p2-arbres-fr.csv"
data = pd.read_csv(filename, encoding='utf-8', sep=';')
print(data)

# # Boxplots

# ## Finding maximum circumference

circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

data.drop(data.index[(data["circonference_cm"] > 120000)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

data.drop(data.index[(data["circonference_cm"] > 30000)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

data.drop(data.index[(data["circonference_cm"] > 10000)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

data.drop(data.index[(data["circonference_cm"] > 3000)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

data.drop(data.index[(data["circonference_cm"] > 1500)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

data.drop(data.index[(data["circonference_cm"] > 800)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

# By reducing the maximum value for maximum circumference, we made a much more readable boxplot that will help us remove absurd values from the database.

data.drop(data.index[(data["circonference_cm"] > 600)], axis=0, inplace=True)
circum_boxplot = data.boxplot(column=['circonference_cm'])
# circum_boxplot
plt.show()

# # Finding maximum height

height_boxplot = data.boxplot(column=['hauteur_m'])
# height_boxplot
plt.show()

data.drop(data.index[(data["hauteur_m"] > 50000)], axis=0, inplace=True)
height_boxplot = data.boxplot(column=['hauteur_m'])
# height_boxplot
plt.show()

data.drop(data.index[(data["hauteur_m"] > 2000)], axis=0, inplace=True)
height_boxplot = data.boxplot(column=['hauteur_m'])
# height_boxplot
plt.show()

data.drop(data.index[(data["hauteur_m"] > 250)], axis=0, inplace=True)
height_boxplot = data.boxplot(column=['hauteur_m'])
# height_boxplot
plt.show()

# By reducing the maximum value for maximum height, we made a much more readable boxplot that will help us remove absurd values from the database.

data.drop(data.index[(data["hauteur_m"] > 150)], axis=0, inplace=True)
height_boxplot = data.boxplot(column=['hauteur_m'])
# height_boxplot
plt.show()

# # Important values

columns = getColumns(data)
row_count = getTreeNumber(data)
PARIS_LOCATION = (48.856614, 2.3522219)

# ## Showing how many values are missing in each column

missing_values = msno.bar(data)


# # Data cleanup

# We remove columns we won't be using for our study, either because they aren't useful or because they aren't filled with enough data.
# We also remove lines that weren't filled correctly, for example if the tree circunference or height is equal to 0, or if the tree is taller or wider than the biggest tree known in Paris.

# Removing unwanted columns from data frame
def cleaningColumns(dataF):
    dataF.drop(['type_emplacement', 'domanialite', 'complement_addresse', 'numero'], axis=1, inplace=True)
    dataF.drop(['id_emplacement', 'variete', 'stade_developpement', 'remarquable'], axis=1, inplace=True)
    return dataF


# Removing unwanted lines from data frame
def cleaningRows(dataF):
    dataF.drop(dataF.index[(dataF["circonference_cm"] <= 0)], axis=0, inplace=True)
    dataF.drop(dataF.index[(dataF["hauteur_m"] <= 0)], axis=0, inplace=True)
    # biggest circumference paris tree 8m -> 800 cm
    dataF.drop(dataF.index[(dataF["circonference_cm"] > 900)], axis=0, inplace=True)
    # tallest paris tree 35 m -> 3500 cm
    dataF.drop(dataF.index[(dataF["hauteur_m"] > 40)], axis=0, inplace=True)
    return dataF

# Data clean up
data = cleaningColumns(data)
data = cleaningRows(data)

# # Data after cleanup

# Save cleaned up csv
data.to_csv('./resources/cleanedDF.csv', encoding='utf-8', sep=';', index=False)
data.reset_index(drop=True)

# # Work on the data

# ## Species percentage in Paris

# Top 10 most present species in Paris
species_group = data.groupby(['espece']).size().sort_values(ascending=False)
species_group.plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.1f%%')
plt.title('Species percentage in Paris')
plt.ylabel('')
plt.savefig("./resources/species_percentage.png")
plt.show()

top_species_df = species_group.head(10).reset_index(name='count')
top_species_list = []
all_species_list = []
print("Every species :")

for index, row in species_group.iterrows():
    specie = species_group['espece'][index]
    all_species_list.append(specie)
    print(specie)

print("Top 10 most present species :")
for index, row in top_species_df.iterrows():
    specie = top_species_df['espece'][index]
    top_species_list.append(specie)
    print(specie)

# ## Species percentage for each district

species_district_df = data.assign(dummy='').groupby(['arrondissement', 'espece']).size().reset_index(name="count")

species_district_df.drop(species_district_df.index[(species_district_df["espece"] not in top_species_list)], axis=0,
                         inplace=True)

for i in range(len(species_district_df)):
    specie = species_district_df["espece"][i]
    district = species_district_df["arrondissement"][i]
    count = species_district_df["count"][i]
    print(district, ":", count, specie)

# reshape the dataframe
species_district_dfpivot = species_district_df.pivot(index=['arrondissement'], columns=['espece'], values='count')

# plot stacked bars
species_district_dfpivot.plot(kind='barh', stacked=True, rot=0, figsize=(10, 4))

# species_district_df.plot(x='arrondissement', kind='bar', stacked=True, xlabel = 'Districts', ylabel='Species frequency')


# ## Tree number percentage per district

# ### On a wheel

# Tree number percentage per 'arrondissement'
district_group = data.assign(dummy='').groupby(['arrondissement']).size().sort_values(ascending=False)
district_group.plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.2f%%')
plt.title('Tree number percentage per district')
plt.ylabel('')
plt.savefig("./resources/tree_number_percentage_per_district.png")
plt.show()

# ### On the map

# Districts' geolocalisation
first_of_each_district_df = data.groupby(['arrondissement']).nth(0).reset_index()
first_of_each_district_df.drop(['id', 'lieu', 'circonference_cm', 'hauteur_m', 'genre', 'espece', 'libelle_francais'],
                               axis=1, inplace=True)

district_geoloc = {}
for i in range(len(first_of_each_district_df)):
    loc_a_index = first_of_each_district_df["geo_point_2d_a"][i]
    loc_b_index = first_of_each_district_df["geo_point_2d_b"][i]
    index = first_of_each_district_df["arrondissement"][i]
    coordinates = (loc_a_index, loc_b_index)
    district_geoloc[index] = coordinates

print(first_of_each_district_df)

# Tree number per district
numb_per_district = data.groupby(['arrondissement']).size()

# Creating map
m = folium.Map(location=[48.856614, 2.3522219], width=750, height=500)

# Placing markers for each district on the map
for index, value in numb_per_district.items():
    if index in district_geoloc:
        localisation = district_geoloc[index]
        text = str(value) + " trees are planted in ", index
        marker = folium.Circle(
            location=localisation,
            radius=value / 10,
            fill=True,
            popup=text
        )
        marker.add_to(m)

# Printing
# m

# ## Tree number percentage per place

# Tree number percentage per place
place_group = data.assign(dummy=1).groupby(['lieu']).size().sort_values(ascending=False)
place_group.head(10).plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.2f%%')
plt.title('Top ten most green place')
plt.ylabel('')
plt.savefig("./resources/top_ten_most_green_places.png")
plt.show()

# ### On the map

# Places' geolocalisation
first_of_each_place_df = data.groupby(['lieu']).nth(0).reset_index()
first_of_each_place_df.drop(
    ['id', 'arrondissement', 'circonference_cm', 'hauteur_m', 'genre', 'espece', 'libelle_francais'], axis=1,
    inplace=True)

place_geoloc = {}
print("Place coordinates")
for i in range(len(first_of_each_place_df)):
    loc_a_index = first_of_each_place_df["geo_point_2d_a"][i]
    loc_b_index = first_of_each_place_df["geo_point_2d_b"][i]
    index = first_of_each_place_df["lieu"][i]
    coordinates = (loc_a_index, loc_b_index)
    place_geoloc[index] = coordinates
    print(index, ':', place_geoloc[index])

trees_per_place = data.assign(dummy=1).groupby(['lieu']).size().sort_values(ascending=False)

# Tree number per place
numb_per_district = data.assign(dummy='').groupby(['arrondissement']).size()

# Creating map
m = folium.Map(location=[48.856614, 2.3522219], width=750, height=500)

"""
# Too long and too heavy for the map

# Placing markers for each district on the map
for index, value in trees_per_place.items():
    if index in place_geoloc:    
        localisation = place_geoloc[index]
        text = str(value) +" % of trees are planted in ", index
        marker = folium.Circle(
                location=localisation, 
                radius=100, 
                fill=True,
                popup=folium.Popup(text, max_width=500)
                )
        marker.add_to(m)

# Printing
m
"""

# ## Average height per arrondissement

# Average height per arrondissement
height_mean = data.groupby(['arrondissement'])['hauteur_m'].mean().reset_index().plot(x='arrondissement',
                                                                                      y='hauteur_m',
                                                                                      kind='bar',
                                                                                      subplots=True,
                                                                                      figsize=(15, 10),
                                                                                      legend=None)
plt.title('Average height per district in meters')
plt.xlabel('Districts')
plt.ylabel('Height in meters')
plt.savefig("./resources/average_height_per_arrondissement.png")
plt.show()

# ## Average circumference per district

# Circumference average per arrondissement
circum_mean = data.groupby(['arrondissement'])['circonference_cm'].mean().reset_index().plot(x='arrondissement',
                                                                                             y='circonference_cm',
                                                                                             kind='bar',
                                                                                             subplots=True,
                                                                                             figsize=(15, 10),
                                                                                             legend=None)
plt.title('Average circumference per district in centimeters')
plt.xlabel('Districts')
plt.ylabel('Circumference in centimeters')
plt.savefig("./resources/average_circumference_per_district.png")
plt.show()
