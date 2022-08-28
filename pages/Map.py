import pandas as pd
import dash
from dash import dcc,callback,html
import dash_bootstrap_components as dbc
import plotly.express as px   
from dash.dependencies import Input, Output
import os
from dotenv import load_dotenv

#Load env variables
load_dotenv()

Fema_Data_Path= os.getenv('Fema_Data_Path')


#import requests

dash.register_page(__name__, path="/fema_map")
# app = dash.Dash(__name__)

disasters_data = pd.read_csv(Fema_Data_Path)

def setup_mapDF(dataFrame,option_selected):
    dff = dataFrame.copy()
    dff = dff[dff['incidentType'] == option_selected]
    prelimQuanity = dff[['state','incidentType','incidentCount']]
    groupBy = prelimQuanity.groupby('state',as_index=False).sum()
    return groupBy

#disasters_requests = requests.get(
#   "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$sortby = state")'

external_stylesheets = [dbc.themes.BOOTSTRAP]

layout = html.Div([
    html.H1("FEMA Disaster Declarations", style={'text-align' : 'center'}),
    html.P("Disaster Type", style= {'margin-top': '5px'}),
    dcc.Dropdown(id="select_type_map",
                options=[{"label": "Tornado", "value": "Tornado"},
                        {"label": "Hurricane", "value": "Hurricane"},
                        {"label": "Flood", "value": "Flood"},
                        {"label": "Fire", "value": "Fire"},
                        {"label": "Severe Storms", "value": "Severe Storm(s)"},
                        {"label": "Drought", "value": "Drought"},
                        {"label": "Coastal Storm", "value": "Coastal Storm"},
                        {"label": "Snow", "value": "Snow"},
                        {"label": "Freezing", "value": "Freezing"},
                        {"label": "Severe Ice Storm", "value": "Severe Ice Storm"},
                ],
                multi=False,
                value="Tornado",
                style={'width':"40%"}),

                html.Br(),

    
                html.Div(
                    dcc.Graph(id='disaster_map_fema', figure={}),
                    className='graphBox'
                ),
                html.Div(
                    dcc.Graph(id="disaster_bar", figure={}),
                    className='graphBox'
                ),
                

                

])    

@callback(
    [
    Output(component_id='disaster_map_fema', component_property='figure'),
    Output(component_id='disaster_bar',component_property='figure')],
    [Input(component_id='select_type_map', component_property='value')],
    
)

def update_graph(option_selected):
    
    

    disasterTypeSum = setup_mapDF(disasters_data,option_selected)

    stateHover = []
    incidentCountHover = []

    #Create a window of time between 2020-2022 x amount of disasters occurred

    
    
    for i in range(len(disasterTypeSum)):

        stateHover.append(disasterTypeSum['state'][i])
        incidentCountHover.append(disasterTypeSum['incidentCount'][i])

    map = px.choropleth(
        data_frame=disasterTypeSum,
        locations="state",
        locationmode='USA-states',
        scope="usa",
        color='incidentCount',
        hover_data=["state","incidentCount"],
        color_continuous_scale=px.colors.sequential.Plotly3,
        labels={'incidentType': 'Incident Type'},
        template='plotly_dark',
        
    )

    #map.update_layout()

    bargraph=px.bar(data_frame=disasterTypeSum, x="state",y="incidentCount")


    return map, bargraph

