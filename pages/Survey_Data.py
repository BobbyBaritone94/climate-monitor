import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px  
from dash.dependencies import Input, Output
import os
from dotenv import load_dotenv

load_dotenv()

Climate_Data_Path= os.getenv('Climate_Data_Yale_Path')
Climate_MetaData_Path=os.getenv('Climate_MetaData_Path')

#import requests

dash.register_page(__name__, path="/survey_data")

# create engine, connection, read_sql for each graph
data = pd.read_csv(Climate_Data_Path,encoding='Latin1')
dfMaster = pd.DataFrame(data)
data = pd.read_csv(Climate_MetaData_Path,encoding='Latin1')
dfMeta = pd.DataFrame(data)
State_Splice= dfMaster[dfMaster['GeoType']=='State']



us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

def getQuestions(metaData):
    optionsList=[]
    for index,row in metaData.iterrows():
        optionsList.append({"label":row['vardesc'],"value":row['ï»¿varname']})
    return optionsList

def setup_map_data(mainData,question,year):
    mainData = mainData[mainData['GeoType'] == 'State']
    mainData = mainData[mainData['ï»¿year'] == year]
    mainData = mainData.replace({'GeoName':us_state_to_abbrev})
    return mainData



layout = html.Div([
    html.H1("Climate Survey Data", style={'text-align' : 'center'}),
    html.P("Questions asked", style= {'margin-top': '5px'}),
    dcc.Dropdown(id="Choose-Question",
    #Get list of options
                options=getQuestions(dfMeta),
                multi=False,
                value="affectweather",          
                className="optionsList"
                ),

    dcc.Slider(id="Choose-Year",
            step=None,
            marks={
                2014: '2014',
                2016: '2016',
                2018: '2018',
                2019: '2019',
                2020: '2020',
                2021: '2021'
            },
            value = 2018
    ),
    

    html.Div(id='Question asked:', children=[]),
    html.Br(),

    dcc.Graph(id="survey_Graph",figure={}),
    dcc.Graph(id='line_states',figure={})
])

def formatMarks(years):
    emptyDict = {}
    for x in years.split(","):
        year = x.replace(",","")
        emptyDict[int(year)] = year
    return emptyDict
    
@callback(
    Output("Choose-Year","marks"),
    Input("Choose-Question","value")
)
def update_slider(question):
    #print(question)
    dfMeta2 = dfMeta[dfMeta["ï»¿varname"]==question]
    #print(dfMeta)
    #dfMeta2["years.avail"].iloc[0]
    return formatMarks(dfMeta2["years.avail"].iloc[0])


@callback(
    [Output("survey_Graph","figure"),
    Output('line_states','figure')],
    Input("Choose-Question","value"),
    Input("Choose-Year","value"),
)
def update_survey_map(question, year):          #no survey data 2021?
                                                # weird survey question geographic name?
    GraphDF=setup_map_data(dfMaster,question,year)

    map_fig=px.choropleth(
        data_frame=GraphDF,
        locations="GeoName",
        locationmode='USA-states',
        scope="usa",
        color=question,
        color_continuous_scale=px.colors.sequential.Plotly3,
        template='plotly_dark',
    )

    dfMeta2 = dfMeta[dfMeta["ï»¿varname"]==question]
    rangeOfQuest=list(formatMarks(dfMeta2["years.avail"].iloc[0]).keys())
    print(rangeOfQuest[::len(rangeOfQuest)-1])

    multi_fig=px.line(
        State_Splice,
        x='ï»¿year',
        y=question,
        facet_col='GeoName',
        facet_col_wrap=5,
        facet_row_spacing=0.02,
        height=2000,
        range_x=rangeOfQuest[::len(rangeOfQuest)-1],
        range_y=[0,100]
    )

    return map_fig, multi_fig
    