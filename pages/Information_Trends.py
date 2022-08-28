import pandas as pd
import plotly.io as pio
import dash
import numpy as np
from dash import dcc, html, callback
import dash_bootstrap_components as dbc
import plotly.express as px  
from dash.dependencies import Input, Output,State
import os
from dotenv import load_dotenv
from datetime import date
# from bertopic import BERTopic
from dash.exceptions import PreventUpdate

load_dotenv()

Newswhip_Data_Path= os.getenv('Newswhip_Data_Path')



dash.register_page(__name__, path="/sources_vs_engagement")

# create engine, connection, read_sql for each graph
data = pd.read_csv(Newswhip_Data_Path,encoding='Latin1')
df = pd.DataFrame(data)

#The only columns currently necessary within the data frame.
NEEDED_COLUMNS=[
    'fb_data.total_engagement_count',
    'tw_data.tw_count',
    'pi_data.pi_count',
    'li_data.li_count',
    'source.publisher',
    'publication_timestamp',
    'MBFC_category',
    'date_time',
    'headline',
    'link',
    'excerpt']



#Will help make reference table
# Creates a seperate table of sources and their MBFC rating
def publisher_bias(dataFrame):
    sourcesAndBias=dataFrame[['source.publisher','MBFC_category']].copy()
    noDupesData= sourcesAndBias.drop_duplicates()
    return noDupesData

#Do data frame manipulations here that do not need to be dynamic.
# Store them in variable so they are ready 
# at load and do not need to be recalculated
updatedDataFrame=df[NEEDED_COLUMNS].copy()       #we only need certain collumns
MBFC_reference= publisher_bias(updatedDataFrame) #makes a reference table
updatedDataFrame['date_time']=updatedDataFrame['date_time'].astype('datetime64[ns]')

# Relationship between whats being reported and what is on "shelldos"
# Binning by the country of origi. Known russian media sources. Here is the view on climate news from different country sources
# Suspicious list of media. Weird climate change websites.
# Showing engagement over time. From a response perspective, preddict if a story is getting what kind of counter response. 
# Cresaing an opportunity to show something gaining. Respond to stories on the field before they get to prevalent.
# Erik backend daily update and server monitoring. Keep in contact for backend development to align our vision
# TODO: Add the titus table that is dependant on the other graphs.
# TODO: Filter sources of child(article vs engagement) by whats chosen in parent dropdown(sources vs engagement).
# TODO: Show enagement by MBFC rating 
# TODO: Filter sources in parent dropdown by MBFC rating
# TODO: Look into refactoring and cleaning up code through imports.



#Completely sets up dataframe for source vs. engagement everytime the callback function is activated.
def setup_source_engagement(dataFrame,time_start,time_end,source_selected,engagement_selected):
    #filter grouped data by chosen source
    selectedData = dataFrame[dataFrame['source.publisher'].isin(source_selected)]
    #filter by date
    timeFrame=selectedData[(selectedData['date_time'] > time_start) & (selectedData['date_time'] < time_end)]
    #group by source and sum
    groupedData= timeFrame.groupby('source.publisher',as_index=False)[engagement_selected].sum()
    #merge table with MBFC_category
    groupedData= groupedData.merge(MBFC_reference,on='source.publisher',how='left')
   
    return groupedData



##Completely sets up dataframe for article vs. engagement everytime the callback function is activated.
def setup_article_engagement(dataFrame,option_selected,percentage_selected,time_start,time_end,engagement_selected):
    
    dataFrame = dataFrame[dataFrame['source.publisher'] == option_selected]
    
    dataFrame=dataFrame[(dataFrame['date_time'] > time_start) & (dataFrame['date_time'] < time_end)]
    
    dataFrame = dataFrame.sort_values(by=engagement_selected,ascending=False)
    
    dataFrame = dataFrame.head(int((len(dataFrame)*(int(percentage_selected)/100))))
    return dataFrame

def setup_bubble_article_engagement(dataFrame,option_selected,percentage_selected,time_start,time_end):
    
    dataFrame = dataFrame[dataFrame['source.publisher'] == option_selected]
    
    dataFrame=dataFrame[(dataFrame['date_time'] > time_start) & (dataFrame['date_time'] < time_end)]
    
    dataFrame = dataFrame.groupby('source.publisher',as_index=False)[['fb_data.total_engagement_count','tw_data.tw_count']].sum()
    
    dataFrame = dataFrame.head(int((len(dataFrame)*(int(percentage_selected)/100))))
    return dataFrame

# This function will cut the headlines down to four words as the headlines are very long.
def setupListForTick(dataFrame):
    temp = dataFrame['headline'].str.split(n=4).tolist()
    newList=[]
    for x in temp:
        newList.append(' '.join(x[0:4]))
    return newList

def setupListForTickDoc(dataFrame):
    temp = dataFrame['document'].str.split(n=4).tolist()
    newList=[]
    for x in temp:
        newList.append(' '.join(x[0:4]))
    return newList


#Organize list of values into a list of options with a matching label and value
def createListOfSets(optionsList):
    newList=[]
    for x in optionsList:
        newList.append({'label':x,'value':x})
    return newList
#############GABRIEL

def createListOfSetsPercent(optionsList):
    newList=[]
    for x in optionsList:
        newList.append({'label':str(x)+'%','value':x})
    return newList

def createSourceOptions():
    sourceDF = MBFC_reference['source.publisher'].copy()
    sourceDF = sourceDF.sort_values()
    print(len(sourceDF))
    return createListOfSets(sourceDF.to_list())

#list of publishers to be loaded into options later
sourceOptions = createSourceOptions()
percentageOptions= createListOfSetsPercent([1,3,5,10,15,25,50,100])

#dictionary to lookup month values for datetime functions
monthDict={
    'Jan':1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5,
    'Jun':6,
    'Jul':7,
    'Aug':8,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12
}


#Relative Engagement Count

###
#Temporary
###


#Load in style sheets from Bootstrap
external_stylesheets = [dbc.themes.BOOTSTRAP]

def card_main(title, excerpt, link, index, listLength ):
    color='green'
    tag='LOW'
    if index/listLength< 0.10:
        color='red'
        tag='HIGH'
    elif index/listLength< 0.30:
        color='yellow'
        tag='MEDIUM'

    return dbc.Card(
    [ 
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            tag,
                            style={
                                'backgroundColor':color,
                                'textAlign':'center'
                            })
                    ]),
                    dbc.Col([
                        html.Div(
                            'Relative Engagement Count',
                            style={
                                'color':color
                            })
                    ])
                ]),
                html.P(
                    title,
                    className="card-text",
                    style={
                        'padding-bottom':'30px',
                    },
                ),
                dbc.Button("Go to article",href=link, color="primary",style={
                    'position':'absolute',
                    'bottom':'20px',
                    'margin-top':'20px'
                }),
            ]
        ),
    ],
    class_name='cardBody'
)

# Relative to total or publisher. Verbage check later.
# Have the team work on explanatory text
# what do we want the text to say and how do we want it to appear
# walk me through upon loading
# Modal on first login?
# Upshot and 538 does a good job guiding you through charts
# Explanatory modals where data comes from. why would you use a tool like log x,y,z
# usability testing. Test smaller components before final product. 
# Change Detection- Flagging anomalies of engagement with climate articles
#TrendAnalysis with anomaly detection on top of that.
# Use flags to help create a report 
# Pagination Fade in and Fade out
# What do we want to do trend analysis(possibly based on historical basis) on and anomaly detection(of 3 standard deviations) on.
#What statistical measures. 

#Html for the page that renders underneath the navbar
layout = html.Div([
    html.Div([
        
        
        html.H1("Publisher Engagement", style={'text-align' : 'right'}),

        dbc.Button(
            "i",
            id="collapse-button",
            className="m-4",
            #olor="primary",
            n_clicks=0,
            style ={    
                        'width':'25px',
                        'height':'25px',
                        'border-radius': '100%',
                        'margin': '20px 0 0 5px',
                        'padding': '0',
                        'font-family': 'Cambria, Cochin, Georgia, Times, Times New Roman, serif',
                        # 'background-color' : 'rgba(255, 222, 173, 0)',
                        # 'color':'black',
                        # 'border': '1px solid black',
                    }
        ),
           
    ], style = {
        'display': 'flex', 
        'justifyContent' : 'center'}
    ),
            # ],
            # className="heading-info",
            
            # ),
    dbc.Collapse(
        html.Div(
                [
                    dbc.Card([

                        html.H4("Date Range", className="card-title"),
                        html.P(
                            "Select start date and end date to filter",
                            className="card-text",
                        )],
                        className="mb-3",
                        style ={
                            "width":"30%"
                        }
                    ),
                    dbc.Card([

                        html.H4("Sources", className="card-title"),
                        html.P(
                            "Filter by sources of information",
                            className="card-text",
                        )],
                        className="mb-3",
                        style ={
                            "width":"30%"
                        }
                    ),
                    dbc.Card([

                        html.H4("Engagement Type", className="card-title"),
                        html.P(
                            "Select social media platfrom engagemnt count",
                            className="card-text",
                        )],
                        className="mb-3",
                        style ={
                            "width":"30%"
                        }
                    ),
                ], style = {
                    "display": "flex",
                    "justifyContent" : "space-between"
                }
            ),
        #dbc.Card(dbc.CardBody("This content is hidden in the collapse")),
        id="collapse",
        is_open=False,
    ),


    html.P("Compare Source Engagement Level", style= {'margin-top': '5px'}),
    # dbc.Row([
    #     # dbc.Col([html.H3("From: "),
    #     # dcc.Dropdown(
    #     #     id='year_start',
    #     #     placeholder='Year',
    #     #     options=[2020,2021,2022],
    #     #     value=2022,
    #     #     multi=False,
    #     #     style={'width':"70%"},
    #     #     ),
    #     # dcc.Dropdown(
    #     #     id='month_start',
    #     #     placeholder='Month',
    #     #     options=list(monthDict.keys()),
    #     #     value='Jan',
    #     #     multi=False,
    #     #     style={'width':"70%"},
    #     # )]),
    #     # dbc.Col([html.H3("To: "),
    #     # dcc.Dropdown(
    #     #     id='year_end',
    #     #     placeholder='Year',
    #     #     options=[2020,2021,2022],
    #     #     multi=False,
    #     #     value=2022,
    #     #     style={'width':"70%"},
    #     #     ),
    #     # dcc.Dropdown(
    #     #     id='month_end',
    #     #     placeholder='Month',
    #     #     options=list(monthDict.keys()),
    #     #     multi=False,
    #     #     value='Jun',
    #     #     style={'width':"70%"},
    #     # )]),
        
    # ]),
    html.Div([
        html.Div([html.H5("Date Range"),
        dcc.DatePickerRange(
            id='datePicker',
            min_date_allowed = date(2017, 1, 1),
            max_date_allowed = date(2022, 12, 30),
            display_format='M-D-Y',
            start_date=date(2017,1,1),
            end_date=date(2022,12,30),
            calendar_orientation='vertical'
        )],
        style={'width':'30%'}),
        html.Div([
            html.H5("Sources"),          
            dcc.Dropdown(id="source_type",
                    options= sourceOptions,
                    multi=True,
                    value=['cnn.com','foxnews.com','nytimes.com','science.org'],
                    ),
        ],style={'width' : '30%'}),
        html.Div([html.H5("Engagement Type"),
        dcc.Dropdown( id = 'engagement_selected',
                    options=[
                        {'label':'Facebook','value':'fb_data.total_engagement_count'},
                        {'label':'Twitter','value':'tw_data.tw_count'},
                        {'label':'Pinterest','value':'pi_data.pi_count'},
                        {'label':'LinkedIn','value':'li_data.li_count'},
                     ],
                    multi=False,
                    value='fb_data.total_engagement_count',
                    placeholder='Social Media',
                    
        )],style={'width' : '30%'}),
    ], style ={
        'display':'flex',
        'justifyContent' : 'space-between'
     }),
    
    html.Br(),
    # 3d BUBBLE GRAPH
    # html.Div(id='output_scatter3d_container', children=[]),#,'display': 'flex', 'align-items': 'center', 'width': '125vw''justify-content': 'center'}),

    # html.H4('Engagement Comparison of Sources', style={'textAlign':'center'}),
    # dcc.Graph(id="Scatter3D_engagement_count", figure={}, style ={'height' : '75vh','width': '80vw','display': 'flex','padding': '10px 100px','justify-content': 'center'}),#,'padding': '10px 500px' 'padding-left': '500px'}),
    html.Div([
        dbc.Col([
            html.H6('Select Chart Type'),
            dcc.RadioItems(id = 'radio_items',
                labelStyle = {"display": "inline-block"},
                options = [ {'label': 'Histogram', 'value': 'histogram'},
                            {'label': 'Bubble chart', 'value': 'bubble'}],
                value = 'histogram',
                ),
            ],style={'width':'40vw'}),
        dbc.Col([
            html.H6('Graph axis scaling'),
            dcc.Checklist(
                ['log x  ', 'log y  ', 'log z  '],
                [],
                id='log-checklist',
        ),
        ])
    ],
    className='fix_settings'),
    
    html.Br(),

    html.Div([
        dcc.Graph(id='disaster_map', 
            figure={'layout' : {'autosize': True}}, 
            style = {
                'padding': '20px',
                'width': '80%',
                'height': '60vh',
                'display':'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
            }, 
            )
        ], #className='graphBox'
        style = {'display' : 'flex',
                'justifyContent' : 'center'
            }
        
    ),
    html.Br(),

    html.Div([
        html.H1("BERTopic Model", style={'text-align' : 'right'}),
        dbc.Button(
            "i",
            id="collapse-button-bert",
            className="m-4",
            #olor="primary",
            n_clicks=0,
            style ={    
                        'width':'25px',
                        'height':'25px',
                        'border-radius': '100%',
                        'margin': '20px 0 0 5px',
                        'padding': '0',
                        'font-family': 'Cambria, Cochin, Georgia, Times, Times New Roman, serif',
                        # 'background-color' : 'rgba(255, 222, 173, 0)',
                        # 'color':'black',
                        # 'border': '1px solid black',
                    }
        ),
     
    ], style = {
        'display': 'flex', 
        'justifyContent' : 'center'}
    ),
    dcc.Dropdown(
        id='switch-bert',
        placeholder='Wassup',
        options=[
             {'label':'2021 Jan-Feb','value':1},
            # {'label':'2021 Mar-Apr','value':2},
            # {'label':'2021 May-Jun','value':3},
            # {'label':'2021 Jul-Aug','value':4},
            # {'label':'2021 Sep-Oct','value':5},
            # {'label':'2021 Nov-Dec','value':6},
            # {'label':'2022 Jan-Feb','value':7}
            ],
        value=1,
        multi=False,
        style={'width':"70%"},
    ),
    dcc.Loading(children=[
        html.Div( id='bert-graphs',
            children=[
                
            ],
            style={
                'display':'flex',
                'flexDirection':'column',
                'justifyContent':'center',
                'alignItems':'center',
                'scrollMarginTop':'20vh'
                
            }
        )
    ]
    ),
    html.Br(),
    html.Div([
        html.Div([
            html.H4('Find Relatated Topic'),
            dcc.Input(id='search-topics',
                type="text", 
                placeholder="", 
                value="biden",
                debounce=True),
        ],style={
            'display':'flex',
            'flexDirection':'column'
        }),
        dcc.Loading(
            html.Div(id='output-topics',children=[],
            style={
                'display':'flex',
                'flexDirection':'row',
                'justifyContent':'space-between'
            })
        )
    ],style={
        'display':'flex',
        'flexDirection':'row',
        'justifyContent':'space-evenly'
    }),
    html.Br(),
    html.Div([

        
        html.H1("Select Cluster", style={'text-align' : 'right'}),
        
          
        dbc.Button(
            "i",
            id="collapse-button-3",
            className="m-4",
            #color="primary",
            n_clicks=0,
            style ={    
                        'width':'25px',
                        'height':'25px',
                        'border-radius': '100%',
                        'margin': ' -10px 10px 0 1000px',
                        'padding': '0',
                        'font-family': 'Cambria, Cochin, Georgia, Times, Times New Roman, serif',
                        #'background-color' : 'rgba(255, 222, 173, 0)',
                        # 'color':'black',
                        # 'border': '1px solid black',
                    }
        ),
        
    ], style = { 
        "display" : "flex",
        "justifyContent": "center"
        }
    
    ),
    dcc.Loading([
        html.Div(id='cluster-info',
        children=[

        ])
    ]),

    html.Div([
        html.Div([
            html.Div([
                html.H4('Select Cluster'),
                dcc.Input(id='select-cluster',type="text", placeholder="", debounce=True),
            ],style={
                'display':'flex',
                'flexDirection':'column'
            }),
            dcc.Graph(id='cluster-engagement',figure={},style={
                'height':'80%'
            })
        ],style={
            'display':'flex',
            'flexDirection':'column',
            'width':'45vw'
            
        }),
        dcc.Loading(
        html.Div([
            dcc.Graph(id='mbfc_engagement_fb',figure={}),
            dcc.Graph(id='mbfc_engagement_tw',figure={})
        ],style={
        'display':'flex',
        'flexDirection':'column',
        'width':'45vw'
        }))

    ],style={
        'display':'flex',
        'flexDirection':'row',
        'justifyContent':'center'
    }),


    html.Br(),
    
    html.Div([

        
        html.H1("Article Engagement", style={'text-align' : 'right'}),
        
          
        dbc.Button(
            "i",
            id="collapse-button-2",
            className="m-4",
            #color="primary",
            n_clicks=0,
            style ={    
                        'width':'25px',
                        'height':'25px',
                        'border-radius': '100%',
                        'margin': ' -10px 10px 0 1000px',
                        'padding': '0',
                        'font-family': 'Cambria, Cochin, Georgia, Times, Times New Roman, serif',
                        #'background-color' : 'rgba(255, 222, 173, 0)',
                        # 'color':'black',
                        # 'border': '1px solid black',
                    }
        ),
        
    ], style = { 
        "display" : "flex",
        "justifyContent": "center"
        }
    
    ),

        dbc.Collapse(
            html.Div(
                    [
                        dbc.Card([

                            html.H4("Date Range", className="card-title"),
                            html.P(
                                "Select start date and end date to filter",
                                className="card-text",
                            )],
                            className="mb-3",
                            style={'width':"30%"}
                        ),
                        dbc.Card([

                            html.H4("Sources", className="card-title"),
                            html.P(
                                "Filter by sources of information",
                                className="card-text",
                            )],
                            className="mb-3",
                            style={'width':"30%"}
                        ),
                        
                    ], style = {
                            "display":"flex",
                            "justifyContent":"space-around"
                        }
                ),
            #dbc.Card(dbc.CardBody("This content is hidden in the collapse")),
            id="collapse-2",
            is_open=False,
        ),

    

    html.Div([
            html.Div([
                html.H4("Publisher", style= {'margin-top': '5px'}),
                dcc.Dropdown(id="select_publisher",
                            placeholder='First pick',
                            multi=False,
                            options=sourceOptions,
                            value='cnn.com'),
            ],style={'width':"30%"}
            ),
            html.Div([
                html.H4("Percentage", style= {'margin-top': '5px'}),
                dcc.Dropdown(id="select_percentage",
                            options= percentageOptions,
                            searchable=True,
                            multi=False,
                            value=3),
            ],style={'width':"30%"}
            ),
    ],style = {
        "display":"flex",
        "justifyContent":"space-around"
    }
    ),
    
    # html.P('Select Chart Type', className = 'fix_label', style = {'color': 'black', 'text-align': 'center'}),
    # dcc.RadioItems(id = 'radio_items_articles',
    #                 labelStyle = {"display": "inline-block"},
    #                 options = [
    #                             {'label': 'Histogram', 'value': 'histogram'},
    #                             {'label': 'Bubble chart', 'value': 'bubble'}],
    #                 value = 'histogram',
    #                 style = {'text-align': 'center', 'color': 'black'}, className = 'dcc_compon'), 
    

    
    html.Br(),
    html.Div([
        dcc.Graph(id='publisher_histog', 
            figure={'layout' : {'autosize': True}}, 
            style = {
                'padding': '20px',
                'width': '80%',
                'height': '60vh',
                'display':'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
            }, 
            )
        ], #className='graphBox'
        style = {'display' : 'flex',
                'justifyContent' : 'center'
            }
        
    ),
    
    html.Br(),
   
    html.Div(
        id='card-grid',
        children=[],
        className='cardGrid'
    ),
    
    

])  

@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#DO NOT DELETE THIS. IT IS THE 3D BUBBLE CHART 

# @callback(    
#     [Output(component_id='output_scatter3d_container', component_property='children'),
#     Output(component_id="Scatter3D_engagement_count", component_property='figure')],
#     [Input(component_id='source_type', component_property='value'),
#     Input('year_start','value'),
#     Input('month_start','value'),
#     Input('year_end','value'),
#     Input('month_end','value')
#     ]
# )
# def update_bar_chart(source_selected,year_start,month_start,year_end,month_end):
#     time_start= datetime.datetime(year_start,monthDict[month_start],1)
#     time_end= datetime.datetime(year_end,monthDict[month_end],1)

#     container = "Source(s): {}".format(source_selected)

#     df = setup_source_engagement(
#             updatedDataFrame,
#             time_start,
#             time_end,
#             source_selected,
#             ['fb_data.total_engagement_count',
#                 'tw_data.tw_count',
#                 'pi_data.pi_count',
#                 'li_data.li_count']
#             )
    

#     df_l = df.sort_values('fb_data.total_engagement_count')

#     # pio.templates['custom'] = go.layout.Template(
#     #         layout_paper_bgcolor='rgba(0,0,0,0)',
#     #         layout_plot_bgcolor='rgba(0,0,0,0)'
#     #     )
#     # pio.templates.default = 'none+custom'

#     fig1 = px.scatter(
#         df_l,
#         x=np.zeros(len(df)),
#         y=pd.qcut(df_l["fb_data.total_engagement_count"], q=5, precision=0).astype(str),
#         size="fb_data.total_engagement_count"
#     )

   

   
#     fig2 = px.scatter_3d(data_frame = df,
#                         x='pi_data.pi_count', 
#                         y='tw_data.tw_count', 
#                         z='li_data.li_count',
#                         color='MBFC_category', 
#                         hover_name='source.publisher', 
#                         size='fb_data.total_engagement_count',
#                         size_max=100)

#     fig2.update_layout(scene = dict(
#                     xaxis_title='Pinterest',
#                     yaxis_title='Twitter',
#                     zaxis_title='LinkedIn'),
#                     width=700,
#                     margin=dict(r=20, b=10, l=10, t=10),
#                     legend=dict(yanchor="top",
#                         y=0.99,
#                         xanchor="left",
#                         x=0.01)
#                     )

#     fig1.update_layout(
#         title_text = 'Facebook',
#         height = 10,
#         width = 10
#     )
    
#     fig = go.Figure(
#         data=[t for t in fig2.data] + [t.update(xaxis="x2", yaxis="y2") for t in fig1.data],
#         layout=fig2.layout,
#     )
    
#     fig.update_layout(
#         xaxis_domain=[0, 0.958],
#         xaxis2={"domain": [0.96, 1], "matches": None, "visible": False},
#         yaxis2={"anchor": "free", "overlaying": "y", "side": "right", "position": 1},
#         showlegend=True        
#     )
         
#     return container, fig



#update source graph

@callback(
    Output(component_id='disaster_map', component_property='figure'),
    [Input(component_id='source_type', component_property='value'),
    # Input('year_start','value'),
    # Input('month_start','value'),
    # Input('year_end','value'),
    # Input('month_end','value'),
    Input('engagement_selected','value'),
    Input('radio_items','value'),
    Input('log-checklist','value'),
    Input('datePicker','start_date'),
    Input('datePicker','end_date')
    ]
)
def update_source_graph(source_selected,engagement_selected,radio_items,log_checklist,startDate,endDate):
    #print(constructSourceQuery(source_selected,startDate,endDate))

    # print(startDate,endDate)
    logX=False
    logY=False
    logZ=False
    for x in log_checklist:
        if x.find('x') != -1:
            logX=True
        if x.find('y') != -1:
            logY=True
        if x.find('z') != -1:
            logZ=True
  
    #prep time selected
    # time_start= datetime.datetime(year_start,monthDict[month_start],1)
    # time_end= datetime.datetime(year_end,monthDict[month_end],1)
    time_start= startDate
    time_end= endDate
   
    #load in dataframe
    
    GraphDF = setup_source_engagement(      ##move into histogram
        updatedDataFrame,
        time_start,
        time_end,
        source_selected,
        engagement_selected)

    GraphBC = setup_source_engagement(      ##move into buble
        updatedDataFrame,
        time_start,
        time_end,
        source_selected,
        ['fb_data.total_engagement_count','tw_data.tw_count'])
    
    if radio_items == 'histogram':
        #create graph
        fig = px.histogram(GraphDF, 
            x=engagement_selected,
            y='source.publisher',
            color='MBFC_category')
    
    
        #clean up axis title
        fig.update_xaxes(title_text='Engagement Count')
        fig.update_yaxes(title_text='Source')

        return fig
    
    elif radio_items == 'bubble':
        fig = px.scatter(GraphBC, 
            x="fb_data.total_engagement_count", 
            y="tw_data.tw_count",
            size='fb_data.total_engagement_count',
            hover_name="source.publisher", 
            color = 'MBFC_category',
            log_x=logX,
            log_y=logY,
            size_max=60)
    
        #clean up axis title
        fig.update_xaxes(title_text='FaceBook Engagement')
        fig.update_yaxes(title_text='Twitter Engagement')

        return fig


def createSimScoreComponent(topicList):

    scoreGrid=[]

    for topic,score in zip(topicList[0],topicList[1]):
        print(topic,score)
        scoreGrid.append(
            html.Div([
                html.H5(f'Topic {topic}'),
                html.H3(f'{round(score*100,2)}%')
            ],style = {
                'marginTop':'20px',
                'marginLeft':'20px',
                'padding': '10px',
                'display':'flex',
                'flexDirection':'column',
                'justifyContent':'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
            }, )
        )

    return scoreGrid

##############
#BERTopic
##############

# @callback(
#     Output('output-topics','children'),
#     [Input('search-topics','value'),
#     Input('switch-bert','value')]
# )
# def findRelatedCluster(word,chosen_model):
#     if word is None:
#         raise PreventUpdate

#     topic_model=BERTopic.load(f'models/Batch{chosen_model}/bert-model')

#     with open(f'models/Batch{chosen_model}/bert-topics', 'rb') as f:
#         topics = np.load(f)


#     print(len(topics))
#     #Grab data by length of topics from dataframe.
#     # Dataframe that is loaded must be the same as the one from batches
#     #Rerun notebook to out put dataframe that is identical to batches



#     #topics_over_time = topic_model.topics_over_time(X.headline.to_list(), topics, X.date_time.to_list(), nr_bins=20)

#     freq=topic_model.get_topic_info()
#     freq.set_index('Topic', inplace=True)
    
#     list_of_topics=topic_model.find_topics(word)
    
#     children=createSimScoreComponent(list_of_topics)

#     return children

#############
##############
#############


###
#TODO: This callback would allow the secondary 
# source dropdown to be dependant on the parent 
# but I need to learn more about chained callbacks
# and store to do this correctly.
###

# #update dropdown based on previous choices.
# @callback(
#     [Output('select_publisher','options')],
#     [Input('source_type','value')]
# )
# def update_dropdown(sources_selected):
#     #print(sources_selected)
#     return createListOfSets(sources_selected)


#TODO: Filter sources present in dropdown by MBFC label
#This should be easier than the above but also requires chained callbacks

@callback(
    Output("collapse-2", "is_open"),
    [Input("collapse-button-2", "n_clicks")],
    [State("collapse-2", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@callback(
    [
    Output(component_id='publisher_histog', component_property='figure'),
    # Output('article_table','data')
    Output('card-grid','children')
    ],
    [Input(component_id='select_publisher', component_property='value'), 
    Input(component_id='select_percentage', component_property='value'),
    # Input('year_start','value'),
    # Input('month_start','value'),
    # Input('year_end','value'),
    # Input('month_end','value'),
    Input('engagement_selected','value'),
    Input('datePicker','start_date'),
    Input('datePicker','end_date')
    # Input('radio_items_articles', 'value')
    ]
)
def update_graph(option_selected,percentage_selected,engagement_selected,startDate,endDate):
    
    #prep time selected
    # time_start= datetime.datetime(year_start,monthDict[month_start],1)
    # time_end= datetime.datetime(year_end,monthDict[month_end],1)
    time_start= startDate
    time_end= endDate

    GraphDF = setup_article_engagement(
        updatedDataFrame,
        option_selected,
        percentage_selected,
        time_start,
        time_end,
        engagement_selected
    )

    # GraphBC = setup_bubble_article_engagement(
    #     updatedDataFrame,
    #     option_selected,
    #     percentage_selected,
    #     time_start,
    #     time_end
    # )  

    
    ###Splice by source
    CardDF = GraphDF[['link','headline','excerpt']].copy()
        

    fig = px.histogram(
        GraphDF,
        x=engagement_selected,
        y='headline',
    )

    fig.update_xaxes(title_text='Engagment Count')
    fig.update_yaxes(title_text='Article')
   

    # fig.update_traces(texttemplate="%{}")
    fig.update_layout(
        yaxis = {
        'tickmode': 'array',
        'tickvals': list(range(len(GraphDF))),
        'ticktext': setupListForTick(GraphDF),
        }
    )

    ### Converts links format to markdown
    #i.e. makes them clickable
    # Temp= TableDF.to_dict('records')

    # for x in Temp:
    #     entry= x['link']
    #     x['link']= f'[{entry}]({entry})'
    
    ###
    Temp=[] 
    for index,row in enumerate(CardDF.iterrows()):
        Temp.append(card_main(row[1]['headline'],row[1]['excerpt'],row[1]['link'],index,len(CardDF)))
        
       

    return fig, Temp

   
@callback(
    Output('bert-graphs','children'),
    Input('switch-bert','value')
)
def update_bert(chosen_model):
    
    # topic_model=BERTopic.load(f'models/Batch{chosen_model}/bert-model')

    # with open(f'models/Batch{chosen_model}/bert-topics', 'rb') as f:
    #     topics = np.load(f)


    # print(len(topics))
    # #Grab data by length of topics from dataframe.
    # # Dataframe that is loaded must be the same as the one from batches
    # #Rerun notebook to out put dataframe that is identical to batches



    # #topics_over_time = topic_model.topics_over_time(X.headline.to_list(), topics, X.date_time.to_list(), nr_bins=20)

    # freq=topic_model.get_topic_info()
    # freq.set_index('Topic', inplace=True)

    with open(f'models/Batch{chosen_model}/visualize_topics.json', 'r') as f:
        fig1 = pio.from_json(f.read())
    with open(f'models/Batch{chosen_model}/visualize_topics_barchart.json', 'r') as f:
        fig2 = pio.from_json(f.read())
    with open(f'models/Batch{chosen_model}/topics_over_time.json', 'r') as f:
        fig3 = pio.from_json(f.read())

    figs=[
        dcc.Graph(figure=fig1,style = {
                'marginTop':'20px',
                'padding': '10px',
                'display':'flex',
                'flexDirection':'column',
                'justifyContent':'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
            }),
        dcc.Graph(figure=fig2,style = {
                'marginTop':'20px',
                'padding': '10px',
                'display':'flex',
                'flexDirection':'column',
                'justifyContent':'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
        }), 
        dcc.Graph(figure=fig3,style = {
                'marginTop':'20px',
                'padding': '10px',
                'display':'flex',
                'flexDirection':'column',
                'justifyContent':'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
        })
        ]
    return figs

@callback(
    [Output('cluster-engagement','figure'),
    Output('mbfc_engagement_fb','figure'),
    Output('mbfc_engagement_tw','figure')],
    [Input('switch-bert','value'),
    Input('select-cluster','value')]
)
def select_cluster_graphs(chosen_model,word):

    if word is None:
        raise PreventUpdate

    if chosen_model is None:
        raise PreventUpdate

    # topic_model=BERTopic.load(f'models/Batch{chosen_model}/bert-model')

    with open(f'models/Batch{chosen_model}/bert-topics', 'rb') as f:
        topics = np.load(f)
    
    data=pd.read_csv(f'Portions/Batch{chosen_model}.csv')

    cluster_DF=pd.DataFrame({
        'topic': topics,
        'document': data.headline, 
        'document_id': data.uuid,
        'fb_engagement': data['fb_data.total_engagement_count'],
        'tw_engagement': data['tw_data.tw_count'],
        'mbfc':data.MBFC_category
        })

    cluster_DF.sort_values(by='fb_engagement')

    cluster_DF= cluster_DF[cluster_DF['topic']==int(word)]

    cluster_eng=px.histogram(
        cluster_DF,
        y = 'document',
        x='fb_engagement',
        title='cluster engagement'
    )

    cluster_eng.update_layout(
        yaxis = {
        'tickmode': 'array',
        'tickvals': list(range(len(cluster_DF))),
        'ticktext': setupListForTickDoc(cluster_DF),
        }
    )

    mbfc_fb= px.pie(
        cluster_DF,
        values='fb_engagement',
        names='mbfc',
        title='MBFC on FB'
    )

    mbfc_tw= px.pie(
        cluster_DF,
        values='tw_engagement',
        names='mbfc',
        title='MBFC on TW'
    )

    return cluster_eng,mbfc_fb,mbfc_tw