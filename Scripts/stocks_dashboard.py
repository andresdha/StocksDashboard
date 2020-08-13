import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_auth
import plotly.graph_objs as go
import pandas_datareader as pdr
from datetime import datetime
from decouple import config
import pandas as pd

#Credential Setup
TIINGO_API_KEY = config('TIINGO_API_KEY')
USER = config('DASHBOARD_USER')
PASSWORD = config('DASHBOARD_PASS')
USER2 = config('DASHBOARD_USER2')
PASSWORD2 = config('DASHBOARD_PASS2')
USERNAME_PASSWORD_PAIRS = [
                            [USER, PASSWORD],
                            [USER2, PASSWORD2]
                        ]



app = dash.Dash()

auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)
server = app.server

nsdq = pd.read_csv('/media/andres/HDD/Documents/Courses/Interactive Dashboards with Plotly and Dash/Resources/Plotly-Dashboards-with-Dash-master/Data/NASDAQcompanylist.csv')
nsdq = nsdq.set_index('Symbol')
options = [dict(label=str(nsdq.loc[tic]['Name']) + tic,
                value= tic) for tic in nsdq.index]

data = [{'x':[1,2], 'y':[3,1]}]
layout = {'title': 'Closing Price'}

app.layout = html.Div([
                html.H1('Stock Ticker Dashboard'),
                html.Div([
                    html.H3(
                        'Enter a Stock Symbol:',
                        style={'paddingRight': '30px'}),
                    dcc.Dropdown(
                        id='stock-picker',
                        options=options,
                        value=['TSLA'],
                        multi=True
                    )
                ], style={'display': 'inline-block',
                          'verticalAlign': 'top',
                          'width':'30%'},
                        ),
                html.Div([
                    html.H3('Select a Start and End Date:'),
                    dcc.DatePickerRange(
                        id='date-picker',
                        min_date_allowed=datetime(2000,1,1),
                        max_date_allowed=datetime.today(),
                        start_date=datetime(2017,1,1),
                        end_date=datetime.today()
                    )
                ], style={'display':'inline-block'}),
                html.Div([
                    html.Button(
                        id='submit-button',
                        n_clicks=0,
                        children='Submit',
                        style={
                            'fontSize':24,
                            'marginLeft': '30px'
                        }
                    )
                ], style={'display':'inline-block'}),
                dcc.Graph(
                    id='my-graph',
                    figure={
                        'data':data,
                        'layout': layout
                    }
                )
            ])

@app.callback(
    Output('my-graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('stock-picker', 'value'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date')
    ]
)
def update_graph(n_clicks, stock_ticker, start_date, end_date):

    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')


    dfs = [pdr.tiingo.TiingoDailyReader(
                        tic,
                        start,
                        end,
                        api_key=TIINGO_API_KEY
                    ).read()
                    for tic in stock_ticker]

    traces = [go.Scatter(
                    x=df.index.get_level_values(level=1),
                    y=df['close'],
                    mode='lines',
                    name=df.index.get_level_values(level=0)[0]
                ) for df in dfs]

    fig = {'data': traces, 'layout': layout}

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
