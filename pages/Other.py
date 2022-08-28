import pandas as pd
import dash
from dash import dcc,callback,html
import dash_bootstrap_components as dbc
import plotly.express as px   
from dash.dependencies import Input, Output
import os
from dotenv import load_dotenv
from datetime import date

#Load env variables
load_dotenv()

Agg_Path= os.getenv('Aggregate_Path')


#import requests

dash.register_page(__name__, path="/Other")
# app = dash.Dash(__name__)

AggDF = pd.read_csv(Agg_Path)
#iqrDF = pd.read_csv('OutputAnomaly/Final_IQR.csv')
#zscoreDF = pd.read_csv('OutputAnomaly/Final_zscore.csv')
dfMain= pd.read_csv('Data/climate_news.csv',encoding='Latin1')

#print(AggDF)
def createListOfSetsPercent(optionsList):
    newList=[]
    for x in optionsList:
        newList.append({'label':str(x)+'%','value':x})
    return newList
percentageOptions= createListOfSetsPercent([1,3,5,10,15,25,50,100])

def setup_df_pie(startDate,endDate):
    mean_df=dfMain[(dfMain['date_time']>startDate) & (dfMain['date_time']<endDate)]
    mean_df=mean_df.groupby('MBFC_category')['fb_data.total_engagement_count'].agg(['sum','count','mean']).reset_index()
    print(mean_df)
    return mean_df


external_stylesheets = [dbc.themes.BOOTSTRAP]

layout=html.Div([

    html.Div([
        html.H5('Line Graph'),
        dcc.Dropdown(
            id='select_y',
            options=[
                {'label':'Proportion to most popular Facebook Articles','value':'Pro_FB_eng'},
                {'label':'Proportion to most popular Twitter Articles','value':'Pro_TW_eng'},
                {'label':'Mean levels of Facebook engagement','value':'Mean_Cli_FB_eng'},
                {'label':'Mean levels of Twitter engagement','value':'Mean_Cli_TW_eng'},
            ],
            value='Pro_FB_eng'
        ),
        
        dcc.Graph(id='line_graph',figure={},style = {
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
    ],style={
        'display':'flex',
        'flexDirection':'column',
        'width':'90vw'
    }),
    html.Br(),
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
                )]),
            html.Br(),
            html.Div([
                dcc.Graph(id='mbfc-pie-iqr',figure={},style={'width':'45vw'}),
                dcc.Graph(id='mbfc-pie-zscore',figure={},style={'width':'45vw'})
            ],style={
                'display':'flex',
                'flexDirection':'row',
                'justifyContent':'center'
            })
            
    ],style={
        'display':'flex',
        'flexDirection':'column',
        'alignItems':'center',
        'width':'90vw'
    }),
    
    
    
    
    
    html.Div([
        html.H5("Media Bias"),
        dcc.Dropdown(
            id='select-mbfc',
            options=[
                {'label':'Center Left','value':'Center_left'},
                {'label':'Pro science','value':'Pro_science'},
                {'label':'Least biased','value':'Least_biased'},
                {'label':'Left','value':'Left'},
                {'label':'not listed','value':'not_listed'},
                {'label':'Center right','value':'Center-right'},
                {'label':'Questionable','value':'Questionable'},
                {'label':'right bias','value':'right_bias'},
                {'label':'Conspiracy','value':'Conspiracy'},
                {'label':'Satire','value':'Satire'},
                {'label':'questionable sources','value':'questionable_sources'},
                {'label':'left bias','value':'left_bias'},
                {'label':'left center bias','value':'left-center_bias'},
                {'label':'least biased','value':'least_biased'},
                {'label':'conspiracy pseudocience','value':'conspiracy-pseudocience'},
                {'label':'right center bias','value':'right-center_bias'},
                {'label':'pro science','value':'pro-science'},
                {'label':'satire','value':'satire'}
            ],
            value='Questionable'
        ),
        html.Div([
                html.H4("Percentage", style= {'margin-top': '5px'}),
                dcc.Dropdown(id="percentage",
                            options= percentageOptions,
                            searchable=True,
                            multi=False,
                            value=1),
            ],style={'width':"30%"}
            ),
        html.P('Selected: ',id='chosen-bias-title'),
        dcc.Graph(id='mbfc-article-engagement',figure={},style = {
                'marginTop':'20px',
                'padding': '10px',
                'display':'flex',
                'height':'80vh',
                'flexDirection':'column',
                'justifyContent':'center',
                'alignItems': 'center',
                'box-shadow': '0px 8px 64px rgba(15, 34, 67, 0.271), 0px 0px 1px rgba(15, 34, 67, 0.08)',
                'borderRadius': '24px',
                'background': '#FFFFFF'
            })
    ])
    
],style={
    'display':'flex',
    'flexDirection':'column'
})

@callback(Output('line_graph','figure'),
    Input('select_y','value'))
def setup_graph(y_axis):
    fig = px.line(
        AggDF,
        x='date_time',
        y=y_axis
    )

    return fig


def setupListForTick(dataFrame):
    temp = dataFrame['headline'].str.split(n=4).tolist()
    newList=[]
    for x in temp:
        newList.append(' '.join(x[0:4]))
    return newList

@callback(
    [Output('mbfc-pie-iqr','figure'),
    Output('mbfc-pie-zscore','figure')],
    [Input('datePicker','start_date'),
    Input('datePicker','end_date')])
def setup_pieCharts(startDate,endDate):
    # df=dfMain[dfMain['uuid'].isin(zscoreDF['uuid'])]
    # df=df[(df['date_time'] > startDate) & (df['date_time'] < endDate)]

    # df2=dfMain[dfMain['uuid'].isin(iqrDF['uuid'])]
    # df2=df2[(df2['date_time'] > startDate) & (df2['date_time'] < endDate)]

    # mbfc_fig=px.pie(
    #     df,
    #     values='fb_data.total_engagement_count',
    #     names='MBFC_category',
    #     title='MBFC breakdown IQR'
    # )

    # poli_fig=px.pie(
    #     df2,
    #     values='fb_data.total_engagement_count',
    #     names='MBFC_category',
    #     title='MBFC breakdown Z-score'
    # )

    df= setup_df_pie(startDate,endDate)
    print(df)
    mbfc_fig=px.pie(
        df,
        values='sum',
        names='MBFC_category',
        title='Sum of each MBFC'
    )

    poli_fig=px.pie(
        df,
        values='mean',
        names='MBFC_category',
        title='Mean of each MBFC'
    )

    

    return mbfc_fig,poli_fig

@callback(
    [Output('mbfc-article-engagement','figure'),
    Output('chosen-bias-title','children')],
    [Input('datePicker','start_date'),
    Input('datePicker','end_date'),
    Input('select-mbfc','value'),
    Input('percentage','value')]
)
def mbfc_articles(startDate,endDate,chosenMbfc,percentage_selected):
    #df=dfMain[dfMain['uuid'].isin(zscoreDF['uuid'])]
    df=dfMain[(dfMain['date_time'] > startDate) & (dfMain['date_time'] < endDate)]
    df=df[df['MBFC_category']==chosenMbfc]
    df = df.sort_values(by='fb_data.total_engagement_count',ascending=False)
    df = df.head(int((len(df)*(int(percentage_selected)/100))))

    fig=px.histogram(
        df,
        x='fb_data.total_engagement_count',
        y='headline'
    )

    category='Selected: '+chosenMbfc

    fig.update_layout(
        yaxis = {
        'tickmode': 'array',
        'tickvals': list(range(len(df))),
        'ticktext': setupListForTick(df),
        }
    )

    return fig, category