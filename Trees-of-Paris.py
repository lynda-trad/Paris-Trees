## Library used

import folium as folium
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import missingno as msno
import dash
from dash import dcc
from dash import html

## Retrieving data from the csv file

filename = "./resources/p2-arbres-fr.csv"
data = pd.read_csv(filename, encoding='utf-8', sep=';')
data


### Useful values

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


columns = getColumns(data)
row_count = getTreeNumber(data)
PARIS_LOCATION = (48.856614, 2.3522219)

## Boxplots

### Finding maximum circumference and height

circum_boxplot_before = px.box(data,
                               y='circonference_cm',
                               labels={'circonference_cm': 'Circumference in centimeters'},
                               title='Circumference boxplot before cleanup',
                               log_y=True)

height_boxplot_before = px.box(data,
                               y='hauteur_m',
                               labels={'hauteur_m': 'Height in meters'},
                               title='Height boxplot before cleanup',
                               log_y=True)

### Showing how much data is missing on each column

msno_fig = px.imshow(data.isnull(), title="Missing values in database")


## Data cleanup

# Removing unwanted columns from data frame
def cleaningColumns(dataF):
    dataF.drop(['type_emplacement', 'domanialite', 'complement_addresse', 'numero'], axis=1, inplace=True)
    dataF.drop(['id_emplacement', 'variete', 'remarquable'], axis=1, inplace=True)
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
data = data.drop_duplicates()

## Data after cleanup

# Save cleaned up csv
data.to_csv('./resources/cleanedDF.csv', encoding='utf-8', sep=';', index=False)
data.reset_index(drop=True)

### Boxplots after cleanup

circum_boxplot_after = px.box(data,
                              y='circonference_cm',
                              labels={'circonference_cm': 'Circumference in centimeters'},
                              title='Circumference boxplot after cleanup',
                              log_y=True)

height_boxplot_after = px.box(data,
                              y='hauteur_m',
                              labels={'hauteur_m': 'Height in meters'},
                              title='Height boxplot after cleanup',
                              log_y=True)
"""
## Work on the data

### Species percentage in Paris

# Top 10 most present species in Paris
species_group = data.groupby(['espece']).size().sort_values(ascending=False)
species_group.plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%1.1f%%')
plt.title('Species percentage in Paris')
plt.ylabel('')
plt.show()

### Ten most present species

top_species_df = species_group.head(10).reset_index(name='count')
top_species_list = []
species_to_delete = []

print("Ten most present species :")
for index, row in top_species_df.iterrows():
    specie = top_species_df['espece'][index]
    top_species_list.append(specie)
    print(specie)

for index, val in species_group.iteritems():
    if index not in top_species_list:
        species_to_delete.append(index)

# ## Ten most present species percentage for each district

# In[83]:


species_district_df = data.groupby(['arrondissement', 'espece'], dropna=True).size().reset_index(name="count")

# Removing species which aren't in top_species_list
for specie in species_to_delete:
    species_district_df.drop(species_district_df.index[(species_district_df["espece"] == specie)], axis=0, inplace=True)

species_district_df

# In[84]:


# reshape the dataframe
species_district_dfpivot = species_district_df.pivot(index=['arrondissement'], columns=['espece'], values='count')

# plot stacked bars
species_district_dfpivot.plot(kind='barh', stacked=True, rot=0, figsize=(15, 10),
                              xlabel='Districts', ylabel='Species frequency')
plt.legend(title="Top 10 most present species in all of Paris")
plt.show()

# ## Tree number percentage per district

# ### Districts' geolocalisation

# In[85]:


first_of_each_district_df = data.groupby(['arrondissement']).nth(0).reset_index()
first_of_each_district_df.drop(
    ['id', 'lieu', 'stade_developpement', 'circonference_cm', 'hauteur_m', 'genre', 'espece', 'libelle_francais'],
    axis=1, inplace=True)

district_geoloc = {}
for i in range(len(first_of_each_district_df)):
    loc_a_index = first_of_each_district_df["geo_point_2d_a"][i]
    loc_b_index = first_of_each_district_df["geo_point_2d_b"][i]
    index = first_of_each_district_df["arrondissement"][i]
    coordinates = (loc_a_index, loc_b_index)
    district_geoloc[index] = coordinates

first_of_each_district_df

# ### District surface

# In[86]:


# Surface in km2
surface_dict = {
    'BOIS DE BOULOGNE': 8.46,
    'BOIS DE VINCENNES': 9.95,
    'HAUTS-DE-SEINE': 176,
    'PARIS 10E ARRDT'	: 2.89,
                'PARIS 11E ARRDT'	 : 3.67,
                'PARIS 12E ARRDT'	 : 16.32,
                'PARIS 13E ARRDT'	 : 7.15,
                'PARIS 14E ARRDT'	 : 5.64,
                'PARIS 15E ARRDT'	 : 8.48,
                'PARIS 16E ARRDT'	 : 7.91,
                'PARIS 17E ARRDT'	 : 5.67,
                'PARIS 18E ARRDT'	 : 6.01,
                'PARIS 19E ARRDT'	 : 6.79,
                'PARIS 1ER ARRDT'	 : 1.83,
                'PARIS 20E ARRDT'	 : 5.98,
                'PARIS 2E ARRDT' 	 : 0.99,
                'PARIS 3E ARRDT' 	 : 1.17,
                'PARIS 4E ARRDT' 	 : 1.60,
                'PARIS 5E ARRDT' 	 : 2.54,
                'PARIS 6E ARRDT' 	 : 2.15,
                'PARIS 7E ARRDT' 	 : 4.09,
                'PARIS 8E ARRDT' 	 : 3.88,
                'PARIS 9E ARRDT' 	 : 2.18,
                'SEINE-SAINT-DENIS'  : 236,
                'VAL-DE-MARNE'       : 245,
                }


# ### Drawing on map

# In[87]:


# Tree number per district
numb_per_district = data.groupby(['arrondissement']).size()

# Creating map
m = folium.Map(location=[48.856614, 2.3522219], width=750, height=500)

# Placing markers for each district on the map
for index, value in numb_per_district.items():
    if index in district_geoloc:
        localisation = district_geoloc[index]
        density = value / surface_dict[index] 
        text = str(value) + " trees are planted in " + index + '. \n ---\nDensity: ' + str \
            (int(density)) +        ' trees per km² - District\'s surface = ' + str(surface_dict[index]) + ' km²'
        marker = folium.Circle(
                    location=localisation, 
                    radius=valu e /10,
            fill=True,
            popup=text
        )
        marker.add_to(m)

# Printing
m

# ## Tree number percentage per place

# In[88]:


# Tree number percentage per place
place_group = data.groupby(['lieu']).size().sort_values(ascending=False)
place_group.head(10).plot(kind='pie', subplots=True, startangle=90, figsize=(15, 10), autopct='%.0f%%')

plt.title('Ten most green places')
plt.ylabel('')
plt.show()

"""

## Height, circumference and development stage scatterplot

scatter = data.groupby(['stade_developpement', 'hauteur_m', 'circonference_cm'], dropna=True).size().reset_index()
sns.set(rc={"figure.figsize": (15, 10)})
ax = sns.scatterplot(data=scatter,
                     x='hauteur_m',
                     y='circonference_cm',
                     hue='stade_developpement')
ax.set(xlabel='Height in meters',
       ylabel='Circumference in centimeters',
       title='Height, circumference and development stage')
plt.legend(loc='upper right', title='Development stage')
# plt.show()

h_c_stage_scatter_fig = px.scatter(scatter,
                                   x="hauteur_m",
                                   y="circonference_cm",
                                   color='stade_developpement',
                                   labels={'stade_developpement': "Development stage",
                                           'hauteur_m': "Height in meters",
                                           'circonference_cm':"Circumference in centimeters"
                                           }
                                   )


### Trees' height and circumference and their development stage
# NOT SURE
"""
ax = sns.lineplot(data=scatter.size(),
                  x='hauteur_m',
                  y='circonference_cm',
                  hue='stade_developpement')
ax.set(xlabel='Height in meters',
       ylabel='Circumference in centimeters',
       title='Height and circumference per development stage')
plt.legend(loc='upper right', title='Development stage')
plt.show()

"""

h_c_stage_fig = px.line(scatter,
                        x='hauteur_m',
                        y='circonference_cm',
                        color='stade_developpement',
                        title="Trees\' height and circumference and their development stage",
                        labels={'stade_developpement': "Development stage",
                                'hauteur_m': "Height in meters",
                                'circonference_cm':"Circumference in centimeters"
                                }
                        )

### Height and circumference average per development stage

sub = data.groupby(['stade_developpement'], dropna=True)['hauteur_m', 'circonference_cm'].mean().reset_index()
# sub['hauteur_cm'] = sub['hauteur_m'] * 100
print(sub)
average_h_c_per_stage = px.line(sub,
                                x='stade_developpement',
                                y=['hauteur_m', 'circonference_cm'],
                                title="Height and circumference average per development stage",
                                labels={'stade_developpement': "Development stage",
                                        'hauteur_m': "Height in meters",
                                        'circonference_cm':"Circumference in centimeters",
                                        'value':'Value',
                                        'variable':'Variable'
                                        }
                                )

### Development stage distribution among districts

height_circum_mean = data.groupby(['arrondissement', 'stade_developpement']).size().reset_index(name="count")
dev_distrib_per_district = px.bar(height_circum_mean,
                                  x="count",
                                  y="arrondissement",
                                  color='stade_developpement',
                                  orientation='h',
                                  title="Development stage distribution among districts",
                                  labels={'arrondissement': "Districts",
                                          'stade_developpement': "Development stage",
                                          'count':"Number of trees"
                                          }
                                  )

### Average height per district

# Average height per arrondissement
height_mean = data.groupby(['arrondissement'])['hauteur_m'].mean().reset_index()
height_mean_fig = px.bar(height_mean,
                         x='arrondissement',
                         y='hauteur_m',
                         title="Average height in m per district",
                         labels={'arrondissement':"Districts",
                                 'hauteur_m':"Average height in meters"
                                 }
                         )

### Average circumference per district

# Circumference average per arrondissement

circum_mean = data.groupby(['arrondissement'])['circonference_cm'].mean().reset_index()
circum_mean_fig = px.bar(circum_mean,
                         x='arrondissement',
                         y='circonference_cm',
                         title="Average circumference in cm per district",
                         labels={'arrondissement':"Districts",
                                 'circonference_cm':"Average circumference in centimeters"
                                 }
                         )

#########################################

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Trees of Paris'),

    # Boxplots before cleanup
    dcc.Graph(
        id='circum_boxplot_before',
        figure=circum_boxplot_before
    ),
    dcc.Graph(
        id='height_boxplot_before',
        figure=height_boxplot_before
    ),

    # Missing values in dataframe
    dcc.Graph(
        id='msno_fig',
        figure=msno_fig
    ),

    html.Div(children='''
    We remove columns we won't be using for our study, either because they aren't useful or 
    because they aren't filled with enough data.
    '''),

    html.Div(children='''
    We also remove lines that weren't filled correctly, for example if the tree circumference or 
    height is equal to 0, or if the tree is taller or wider than the biggest tree known in Paris.
    '''),

    # Boxplots after cleanup
    dcc.Graph(
        id='circum_boxplot_after',
        figure=circum_boxplot_after
    ),
    dcc.Graph(
        id='height_boxplot_after',
        figure=height_boxplot_after
    ),

    # Height, circumference and development stage scatterplot
    dcc.Graph(
        id='h_c_stage_scatter_fig',
        figure=h_c_stage_scatter_fig
    ),

    # Trees' height and circumference and their development stage
    # NOT SURE
    dcc.Graph(
        id='h_c_stage_fig',
        figure=h_c_stage_fig
    ),

    # Height and circumference average per development stage
    dcc.Graph(
        id='average_h_c_per_stage',
        figure=average_h_c_per_stage
    ),

    # Development stage distribution among districts
    dcc.Graph(
        id='dev_distrib_per_district',
        figure=dev_distrib_per_district
    ),

    # Average height per district
    dcc.Graph(
        id='height_mean',
        figure=height_mean_fig
    ),

    # Average circumference per district
    dcc.Graph(
        id='circum_mean',
        figure=circum_mean_fig
    )

])

if __name__ == '__main__':
    app.run_server(debug=True)
