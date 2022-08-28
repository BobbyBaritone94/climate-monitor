import dash
from dash import html, callback
import dash_bootstrap_components as dbc
import os
from dotenv import load_dotenv


dash.register_page(__name__, path="/")

load_dotenv()

Newswhip_Data_Path = os.getenv('Newswhip_Data_Path')


# alchemyEngine   = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}', pool_recycle=3600);
# dbConnection    = alchemyEngine.connect()
# dataFrame       = pd.read_sql("select * from source", dbConnection);
# print(dataFrame.head(10))

layout = dbc.Col(
    children=[
        html.Div(
        style={
            'backgroundImage': "url('/assets/MM-home-bg.png')",
            'backgroundRepeat': 'no-repeat',
            'backgroundPosition': 'center',
            'backgroundSize': "cover",
            'width':'auto',
            'height':'30vh',
            'display':'flex',
            'justifyContent':'center',
            'alignItems':'center'
        },
        children=[
            html.H1("Monitoring and Mitigating Misinformation",
            style={
                'textAlign':'center',
                'color':'white'
                }),
        ]),
        html.H3("What is Monitoring and Mitigating Misinformation",
            style={
            'fontFamily': 'Inter',
            'fontStyle': 'normal',
            'fontWeight': '700',
            'fontSize': '24px',
            'lineHeight': '22px',
            'color': '#53686A',
            'textAlign':'center',
            'marginTop':'2em',
            'marginBottom':'1em'
        }),
        html.P('The monitoring and mitigating information project aims to spread awareness about' 
                'climate misinformation and the public perception of climate related issues. User’s are'
                'able to interact with the engagement types of different sources and compare them '
                'visually with either a histogram or a bubble chart. There is also a chart comparing the'
                'engagement level of different articles from a publisher and links to the categorized '
                'articles below. Various climate disaster types can also be found on a United States '
                'map with the number of incidents separated by states. Estimates of the public’s opinion'
                'on certain climate questions can also be seen on the survey data page',
                style={
                    'width':'90vw',
                    'color': '#53686A',
                    'marginLeft':'auto',
                    'marginRight':'auto',
                    'marginBottom': '5vh'
                }),
        html.Div([
            dbc.Col([
                html.H5("Our Data Sources"),
                html.P('The survey data of climate opinions was conducted by the Yale Program on '
                        'Climate Change Communication and their most recent climate opinion map can'
                        'be found at https://climatecommunication.yale.edu/visualizations-data/ycom-us/.'
                        'Disaster data was collected by the Federal Emergency Management Agency which'
                        'is part of the Department of Homeland Security and helps people with disaster'
                        'problems. The article and publisher engagement data was found through NewsWhip,'
                        'a real-time media monitoring platform.',
                    className='home-info-box')
            ]),
            dbc.Col([
                html.H5("Our Process"),
                html.P('Monitoring and Mitigating Misinformation scrapes the most frequently visited '
                        'news sources for articles relating to climate change. In this regard, an algorithm'
                        'is applied to categorize articles into political affiliation based on what political'
                        'values the article is seen to follow. Monitoring and Mitigating Misinformation '
                        'follows engagement in regards to these articles, ordering the articles from most to'
                        'least engaged with articles.',
                    className='home-info-box')
            ]),
            dbc.Col([
                html.H5("Our Data Sources"),
                html.P('sit amet, consectetur adipiscing elit, sed do eiusmod '
                    'tempor incididunt ut labore et dolore magna aliqua. Ut enim '
                    'ad sit amet, consectetur adipiscing elit, sed do eiusmod tempor'
                    ' incididunt ut labore et dolore magna aliqua. Ut enim ad',
                    className='home-info-box')
            ]),
        ],style={
            'width':'90vw',
            'display':'flex',
            'justifyContent':'space-evenly',
            'marginRight':'auto',
            'marginLeft':'auto'
        }),
        html.Div(
        className='home-container graphBox',
        children=[
            html.Div(
                className='home-input',
                children=[
                html.H6("Have any questions?"),
                dbc.Input(placeholder="Can't find the answers you're looking for?")
            ]),
            html.Div(
                className='home-button',
                children=[
                dbc.Button('Get in touch')
            ])    
        ]),
       
])   

