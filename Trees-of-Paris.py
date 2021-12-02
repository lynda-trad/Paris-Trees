## Library used

import folium as folium
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
from dash import dash_table
from dash import dcc
from dash import html
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

## Retrieving data from the csv file

filename = "./resources/p2-arbres-fr.csv"
data = pd.read_csv(filename, encoding='utf-8', sep=';')
data_first = data


# Useful values

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

# Boxplots

# Finding maximum circumference and height

boxplots_before = px.box(data,
                         y=['circonference_cm', 'hauteur_m'],
                         labels={'circonference_cm': 'Circumference in centimeters',
                                 'hauteur_m': 'Height in meters'
                                 },
                         title='Circumference and height boxplot before cleanup',
                         log_y=True)

# Showing how much data is missing on each column

msno_before_fig = px.imshow(data.isnull(), title="Missing values in database")


# Data cleanup

# Removing unwanted columns from data frame
def cleaningColumns(dataF):
    dataF.drop(['type_emplacement', 'complement_addresse', 'numero'], axis=1, inplace=True)
    dataF.drop(['id_emplacement', 'variete', 'remarquable'], axis=1, inplace=True)
    return dataF


# Removing unwanted lines from data frame
def cleaningRows(dataF):
    # biggest circumference paris tree 8m -> 800 cm
    dataF.drop(dataF.index[(dataF["circonference_cm"] > 900)], axis=0, inplace=True)
    # tallest paris tree 35 m -> 3500 cm
    dataF.drop(dataF.index[(dataF["hauteur_m"] > 40)], axis=0, inplace=True)
    return dataF


# Data clean up
data = cleaningColumns(data)
data = cleaningRows(data)
data = data.drop_duplicates()

# Replacing nan values with median
circum_median = data['circonference_cm'].median()
height_median = data['hauteur_m'].median()

data['circonference_cm'] = data['circonference_cm'].replace(0, circum_median)
data['hauteur_m'] = data['hauteur_m'].replace(0, height_median)

msno_after_fig = px.imshow(data.isnull(), title="Missing values in database")

# Boxplots after cleanup

boxplots_after = px.box(data,
                        y=['circonference_cm', 'hauteur_m'],
                        labels={'circonference_cm': 'Circumference in centimeters',
                                'hauteur_m': 'Height in meters'
                                },
                        title='Circumference and height boxplot after cleanup',
                        width=500,
                        log_y=True)

# Species distribution in Paris

species_group = data.groupby(['espece']).size().sort_values(ascending=False).reset_index(name='count')

species_distrib_fig = px.histogram(species_group,
                                   x='espece',
                                   y='count',
                                   labels={'espece': "Species",
                                           'count': "tree count"},
                                   title='Species distribution in Paris',
                                   height=700,
                                   width=1000
                                   )

# Species distribution in each district

species_district_df = data.groupby(['arrondissement', 'espece'], dropna=True).size().sort_values(
    ascending=False).reset_index(name="count")

species_district_fig = px.bar(species_district_df,
                              x="count",
                              y="arrondissement",
                              color='espece',
                              orientation='h',
                              barmode='stack',
                              labels={'arrondissement': "Districts",
                                      'espece': "species",
                                      'count': "Number of trees"
                                      },
                              height=700,
                              title="Species distribution in each district"
                              )

# Tree number percentage per district on the map

# Districts' geolocalisation

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

#### District surface

# Surface in km2
surface_dict = {'BOIS DE BOULOGNE': 8.46,
                'BOIS DE VINCENNES': 9.95,
                'HAUTS-DE-SEINE': 176,
                'PARIS 10E ARRDT': 2.89,
                'PARIS 11E ARRDT': 3.67,
                'PARIS 12E ARRDT': 16.32,
                'PARIS 13E ARRDT': 7.15,
                'PARIS 14E ARRDT'	: 5.64,
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

### Drawing on map

# Tree number per district
numb_per_district = data.groupby(['arrondissement']).size()

# Creating map
paris_map = folium.Map(location=[48.856614, 2.3522219],
                       title="Trees\' density and number per district")

# Placing markers for each district on the map
for index, value in numb_per_district.items():
    if index in district_geoloc:
        localisation = district_geoloc[index]
        density = value / surface_dict[index] 
        text = str(value) + " trees are planted in " + index + '. \n ---\nDensity: ' + str(int(density))\
               + " trees per km² - District\'s surface = " + str(surface_dict[index]) + ' km²'
        marker = folium.Circle(location=localisation,
                               radius=value/10,
                               fill=True,
                               popup=text
                               )
        marker.add_to(paris_map)

paris_map.save("./resources/paris_map.html")

## Show all the trees on the map

all_trees_map = px.scatter_mapbox(data,
                                  lat="geo_point_2d_a",
                                  lon="geo_point_2d_b",
                                  color = 'arrondissement',
                                  hover_name='arrondissement',
                                  hover_data=['circonference_cm', 'hauteur_m', 'lieu'],
                                  color_continuous_scale=px.colors.cyclical.IceFire,
                                  zoom=11,
                                  mapbox_style="open-street-map",
                                  width=1000,
                                  height=1000,
                                  title='Every tree on Paris\' map')
"""
# Choroplet map

choro_map = px.choropleth_mapbox(data,
                                 locations=["geo_point_2d_a", "geo_point_2d_b"],
                                 color='hauteur_m',
                                 color_continuous_scale="Viridis",
                                 range_color=(0, 12),
                                 mapbox_style="open-street-map",
                                 zoom=3,
                                 center={"lat": PARIS_LOCATION[0], "lon":  PARIS_LOCATION[1]},
                                 opacity=0.5,
                                 labels={'hauteur_m':'Height in meters'}
                                 )
choro_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
choro_map.show()
"""
## Height, circumference and development stage scatterplot

scatter = data.groupby(['stade_developpement', 'hauteur_m', 'circonference_cm'], dropna=True).size().reset_index()

h_c_stage_scatter_fig = px.scatter(scatter,
                                   x="hauteur_m",
                                   y="circonference_cm",
                                   color='stade_developpement',
                                   labels={'stade_developpement': "Development stage",
                                           'hauteur_m': "Height in meters",
                                           'circonference_cm': "Circumference in centimeters"
                                           },
                                   title="Height, circumference and development stage scatterplot",
                                   height=800
                                   )
"""
### Trees' height and circumference and their development stage

h_c_stage_fig = px.line(scatter,
                        x='hauteur_m',
                        y='circonference_cm',
                        color='stade_developpement',
                        title="Trees\' height and circumference and their development stage",
                        labels={'stade_developpement': "Development stage",
                                'hauteur_m': "Height in meters",
                                'circonference_cm': "Circumference in centimeters"
                                }
                        )
"""
### Height and circumference average per development stage

sub = data.groupby(['stade_developpement'], dropna=True)['hauteur_m', 'circonference_cm'].mean().reset_index()
# sub['hauteur_cm'] = sub['hauteur_m'] * 100
average_h_c_per_stage = px.histogram(sub,
                                     x='stade_developpement',
                                     y=['hauteur_m', 'circonference_cm'],
                                     title="Height and circumference average per development stage",
                                     labels={'stade_developpement': "Development stage",
                                             'hauteur_m': "Height in meters",
                                             'circonference_cm': "Circumference in centimeters",
                                             'value': 'Value',
                                             'variable': 'Variable'
                                             },
                                     width=900,
                                     height=700
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
                                          'count': "Number of trees"
                                          },
                                  height=800
                                  )

### Average height per district

height_mean = data.groupby(['arrondissement'])['hauteur_m'].mean().reset_index()
height_mean['hauteur_cm'] = height_mean['hauteur_m'] * 100 # converting meters to centimeters
height_mean_fig = px.bar(height_mean,
                         x='arrondissement',
                         y='hauteur_m',
                         title="Average height in m per district",
                         labels={'arrondissement': "Districts",
                                 'hauteur_m': "Average height in meters"
                                 }
                         )

### Average circumference per district

circum_mean = data.groupby(['arrondissement'])['circonference_cm'].mean().reset_index()
circum_mean_fig = px.bar(circum_mean,
                         x='arrondissement',
                         y='circonference_cm',
                         title="Average circumference in cm per district",
                         labels={'arrondissement': "Districts",
                                 'circonference_cm': "Average circumference in centimeters"
                                 }
                         )

# Average circumference/height per district
circum_height_mean_fig = go.Figure()
circum_height_mean_fig.add_trace(go.Bar(name='Cicumference in centimeters',
                                        x=circum_mean['arrondissement'],
                                        y=circum_mean['circonference_cm']),
                                 )

circum_height_mean_fig.add_trace(go.Bar(name='Height in meters',
                                        x=height_mean['arrondissement'],
                                        y=height_mean['hauteur_m']),
                                 )

circum_height_mean_fig.update_traces(overwrite=True)
circum_height_mean_fig.update_xaxes(title_text="Districts", showgrid=False)
circum_height_mean_fig.update_yaxes(title_text="Average in centimeters/meters", showgrid=False)
circum_height_mean_fig.update_layout(title_text="Average circumference and height per district")

### Domain distribution in districts

domain_district = data.groupby(['arrondissement', 'domanialite'], dropna=True).size().reset_index(name='count')
domain_treemap_fig = px.treemap(domain_district,
                                path=['arrondissement', 'domanialite'],
                                values='count',
                                title='Domain distribution in districts')

#########################################

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    # Title

    html.H1(children='Trees of Paris',
            style={
                'textAlign': 'center'
                }
            ),

    # Description

    html.Div(children=
             '''We have a csv file in which a dataframe is filled with information about registered trees in Paris.
             The objective of this data visualisation is to find a more effective way to maintain trees 
             and save money and time while doing so.''',
             ),

    # Summary

    html.H1(children='''Summary''',
            style={
                'textAlign': 'center'
            }
            ),

    html.Div(children='''
    * Data cleanup 
    * Circumference and height boxplot
    * NaN values Heatmap
    * Districts’ tree number and tree density on the map
    * Species distribution among districts and in Paris
    * Scatterplot : height and circumference per development stage
    * Height and circumference per development stage
    * Average height and circumference per district
    * Development stage distribution among districts
    * Treemap : domain distribution among districts
    '''),

    # Data before cleanup

    html.H1(children='''Dataframe before cleanup''',
            style={
                'textAlign': 'center'
            }
            ),

    dash_table.DataTable(
        id='data_first',
        columns=[{"name": i, "id": i} for i in data_first.columns],
        data=data_first.to_dict('records'),
        page_size=10,
    ),


    # Boxplots before cleanup

    html.H1(children='''Boxplots before cleanup''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='circum_boxplot_before',
        figure=boxplots_before
    ),

    html.Div(children='''
    With circumference and height boxplots, we find out ouliers : 
    they are trees whose height or circumference are too far from the average tree. 
    This way we can find an approximate maximum value for each column and remove outliers trees.
    '''),

    # Missing values in dataframe before cleanup

    html.H1(children='''Missing values in dataframe before cleanup''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='msno_before_fig',
        figure=msno_before_fig
    ),

    html.Div(children='''
    We remove columns we won't be using for our study, either because they aren't useful or 
    because they aren't filled with enough data.
    '''),

    html.Div(children='''
    We also remove lines that weren't filled correctly, for example if the tree circumference or 
    height is equal to 0, or if the tree is taller or wider than the biggest tree known in Paris.
    '''),

    html.Div(children='''
    We finally replace the missing values in the circumference and height columns with their corresponding median.
    '''),

    # Dataframe after cleanup

    html.H1(children='''Dataframe after cleanup''',
            style={
                'textAlign': 'center'
            }
            ),

    dash_table.DataTable(
        id='dataframe',
        columns=[{"name": i, "id": i} for i in data.columns],
        data=data.to_dict('records'),
        page_size=10,
    ),

    # Boxplots after cleanup

    html.H1(children='''Boxplots after cleanup''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='circum_boxplot_after',
        figure=boxplots_after
    ),

    html.Div(children='''
    After cleaning the data, we can notice the boxplots are shorter and the heatmap is more filled.
    '''),

    # Missing values in dataframe after cleanup

    html.H1(children='''Missing values in dataframe after cleanup''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='msno_after',
        figure=msno_after_fig
    ),

    html.Div(children='''
    Thanks to the heatmap, we find out which columns are empty or are missing too many values for our work.
    '''),

    # Species distribution in Paris

    html.H1(children='''Species distribution in Paris''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='species_distrib',
        figure=species_distrib_fig
    ),

    html.Div(children='''
    This graph shows which species appear the most in Paris.
    '''),

    # Species distribution in each district

    html.H1(children='''Species distribution in each district''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='species_district',
        figure=species_district_fig
    ),

    html.Div(children='''
    This shows the species distribution among districts. 
    If a certain species have special requirement, we will calculate the budget needed to take care of it. 
    It also helps if we want to make some districts more diverse or add more of a certain species.
    '''),

    # Paris map

    html.H1(children='''Trees\' density and number per district on the map''',
            style={
                'textAlign': 'center'
            }
            ),

    html.Iframe(
        id='paris_map',
        srcDoc=open("./resources/paris_map.html", 'r').read(),
        width='100%',
        height='500'
    ),

    html.Div(children='''
    This map shows the tree density of each district, with the tree total count. 
    This way, we can choose to make the district greener by planting trees if there aren't enough, we can also choose 
    where to employ the most people because some districts require more work than others.
    '''),

    # Every tree map

    html.H1(children='''Every tree and their district on Paris' map''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='all_trees_map',
        figure=all_trees_map
    ),

    html.Div(children='''
    We get a better picture of where trees are placed by showing every tree on Paris' map.
    '''),

    # Height, circumference and development stage scatterplot

    html.H1(children='''Height, circumference and development stage scatterplot''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='h_c_stage_scatter',
        figure=h_c_stage_scatter_fig
    ),

    html.Div(children='''
    The scatterplot shows every tree with their development stage, 
    their height in meters and circumference in centimeters. 
    This way we can find out strange values like a young tree whose circumference is at 800 centimeters ! 
    We can also point out the correlation between age and size.
    '''),

    # Height and circumference average per development stage

    html.H1(children='''Height and circumference average per development stage''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='average_h_c_per_stage',
        figure=average_h_c_per_stage
    ),

    html.Div(children='''
    This barplot shows the average circumference and height per development stage. 
    This shows the correlation between size and age.
    '''),

    # Development stage distribution among districts

    html.H1(children='''Development stage distribution among districts''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='dev_distrib_per_district',
        figure=dev_distrib_per_district
    ),

    html.Div(children='''
    The stacked bars show the development stage distribution among districts. 
    With this information, we can figure out the frequency of the maintenance since older 
    or younger trees might need more or less work done on them compared to others.
    '''),

    # Average circumference/height per district

    html.H1(children='''Average circumference/height per district''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='circum_height_mean_fig',
        figure=circum_height_mean_fig
    ),

    # Average height per district

    html.H1(children='''Average height per district''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='height_mean',
        figure=height_mean_fig
    ),

    # Average circumference per district

    html.H1(children='''Average circumference per district''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='circum_mean',
        figure=circum_mean_fig
    ),

    html.Div(children='''
    The barplots show the average circumference and height for every district. 
    This helps figure out which district will need workers to trim trees more often than others for example.
    '''),

    # Domain distribution in districts

    html.H1(children='''Domain distribution among districts''',
            style={
                'textAlign': 'center'
            }
            ),

    dcc.Graph(
        id='domain_treemap',
        figure=domain_treemap_fig
    ),

    html.Div(children='''
    This treemap shows the domain distribution in districts: this helps know when 
    to use trucks to stop on the road and trim trees for example, which means more 
    budget will be needed in the said district. It also shows which districts have the most trees.
    '''),

    # Conclusion

    html.H1(children='''Conclusion''',
            style={
                'textAlign': 'center'
            }
            ),

    html.Div(children='''
    We found correlation between height, circumference and age, we also showed where the biggest trees are in order to help the direction find where to send the most employees to maintain trees.
    We still need to add :
    - pairplots.
    - a choroplet map to show the tree density of each district in a way.
    - buttons to make the figures more user-friendly and accessible.
    '''),
])

if __name__ == '__main__':
    app.run_server(debug=True)
