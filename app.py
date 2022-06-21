"""
app.py

Main program that starts the Dash app locally. 

If there is no saved csv file to load in DataFrame, generates one using files located in the assets folder.
"""

# Dash and Plotly imports
import dash
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np

# Image related imports
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import pillow_heif
pillow_heif.register_heif_opener()

# Etc 
import os
from pathlib import Path
from datetime import datetime
import photos_util

# path to the photos folder which should be located in same dir as app.py
# this is where the photos are read from
ASSETS_PATH = Path(os.getcwd())/'assets'

# look for mapbox access token used for generating the map
# todo: could alter so that if no mapbox, uses default plotly geomap
if not os.path.exists(Path(os.getcwd())/'mapbox_token'):
    print(f"No mapbox token found in {os.getcwd()}. Unable to generate map. Exiting...")
    exit(1)
else:
    MAPBOX_TOKEN=open("mapbox_token").read()

    
# regions used for dropdown menu for centering map
regions = {
    "world": {"lat": 0, "lon": 0, "zoom": 1},
    "europe": {"lat": 50.3785, "lon": 14.9706, "zoom": 3},
    "usa": {"lat": 37.0902, "lon": -95.7129, "zoom": 3},
    "rome": {"lat": 41.902782, "lon": 12.496366, "zoom": 11},
    "pompeii": {"lat": 40.7510, "lon": 14.4870, "zoom": 12},
    "florence": {"lat": 43.769562, "lon": 11.255814, "zoom": 11},
    "antibes": {"lat": 43.56241, "lon": 7.10831, "zoom": 11},
    "mallorca":{"lat": 39.710358,"lon": 2.995148, "zoom": 9},
    "barcelona":{"lat": 41.390205,"lon": 2.154007, "zoom": 12},
}


# Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash("Photo Map Viewer", external_stylesheets=external_stylesheets)
server = app.server


def get_df() -> pd.DataFrame:
    """Returns DataFrame containing photo info"""
    cur_dir = Path(os.getcwd())
    if os.path.exists(cur_dir/'saved_df.csv'):
        df = pd.read_csv(cur_dir/'saved_df.csv')
    else:
        photo_list = photos_util.get_photos_from_path(ASSETS_PATH)
        df = photos_util.construct_df(photo_list)
        # make day column string based and minimize to start with 1
        df.day = df.day - (df.day.min() - 1)
        df.day = df.day.astype(str)
        df.to_csv(cur_dir/'saved_df.csv', index=False)
    return df


def create_figure(df: pd.DataFrame):
    """Returns mapbox figure using dataframe."""
    px.set_mapbox_access_token(MAPBOX_TOKEN)
    fig = px.scatter_mapbox(df, lat=df.latitude, lon=df.longitude,     
                            color="day", hover_name='datetime',
                            hover_data=["latitude", "longitude"],
                           zoom=1)

    fig.update_geos(projection_type="natural earth",
                #projection_type="orthographic",
                #fitbounds="locations",
                visible=True,
                resolution=110,
                showcountries=True)


    fig.update_layout(height=600, margin={"r":0,"t":0,"l":0,"b":0})
    fig.update(layout_coloraxis_showscale=False)
    return fig

# set dataframe and figure
df = get_df()
fig = create_figure(df)


app.layout = html.Div(children=[
    html.H1(children='Photo Map Viewer', style={'textAlign': 'center'}),
    html.Div(children='''
        Uses extracted GPS info from photos to plot them on the map.
        Click on any point to show the photo taken there!
    ''', style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='dropdown-map-region',
        value='world',
        options=[
            {"label": "World", "value": "world"},
            {"label": "Europe", "value": "europe"},
            {"label": "United States", "value": "usa"},
            {"label": "Rome, Italy", "value": "rome"},
            {"label": "Pompeii, Italy", "value": "pompeii"},
            {"label": "Florence, Italy", "value": "florence"},
            {"label": "Antibes, France", "value": "antibes"},
            {"label": "Mallorca, Spain", "value": "mallorca"},
            {"label": "Barcelona, Spain", "value": "barcelona"},
        ],
        style={'width': '50%', 'margin-bottom':'10px',},
    ),

    html.Div(children=[
        dcc.Graph(
            id='Map',
            figure=fig,
            style={'display': 'inline-block',
                  'height':'75vh',
                  'width':'50%'}
        ), 

        html.Img(id="html-img", src='', 
                 style={'height':'fit-content',
                        'max-width':'calc(50% - 10px)',
                        'max-height':'75vh',
                       'display': 'inline-block',
                        'border': 'black 10px solid',
                       'margin':'auto',}),
    ], style={'display':'flex'},)

])


@app.callback(
    Output('Map', 'figure'),
    Input('dropdown-map-region', 'value')
)
def center_map_region(region):
    """Center the mapbox view on selected region"""
    fig.update_mapboxes(center={'lat': regions[region]['lat'],
                        'lon': regions[region]['lon']},
                        zoom=regions[region]['zoom'])
    return fig


@app.callback(
    Output("html-img", 'src'),
    [Input('Map', 'clickData')],
    [dash.State('Map', 'figure')]
)
def show_html_img(clickData, fig):
    """Show image of the data point when clicked on in the mapbox"""
    if clickData:
        point = clickData['points'][0]
        p_datetime = point['hovertext']
        p_lat = point['lat']
        p_lon = point['lon']
        
        img_name = df[(df['datetime'] == p_datetime) & (df['latitude'] == p_lat) & (df['longitude'] == p_lon)]['filename'].values[0]
        if img_name.endswith('.heic'):
            # use converted image instead
            img_name = img_name.replace('.heic', '.jpg')
        return app.get_asset_url(img_name)
    else:
        return ""


if __name__ == "__main__":
    app.run_server(debug=True)