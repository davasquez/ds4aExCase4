import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_table

df = pd.read_csv('aggr.csv', parse_dates=['Entry time'])
df['year_month'] = df.apply(lambda row: row['Entry time'].strftime("%Y-%m"), axis=1)
df['Entry time date'] = pd.to_datetime(df['Entry time'].map(lambda x: "{}-{}-{}".format(x.year, x.month, x.day)))

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/uditagarwal/pen/oNvwKNP.css', 'https://codepen.io/uditagarwal/pen/YzKbqyV.css'])

app.layout = html.Div(children=[
    html.Div(
            children=[
                html.H2(children="Bitcoin Leveraged Trading Backtest Analysis", className='h2-title'),
            ],
            className='study-browser-banner row'
    ),
    html.Div(
        className="row app-body",
        children=[
            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding row",
                        children=[
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Exchange",),
                                    dcc.RadioItems(
                                        id="exchange-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['Exchange'].unique()
                                        ],
                                        value='Bitmex',
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Leverage",),
                                    dcc.RadioItems(
                                        id="leverage-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['Margin'].unique()
                                        ],
                                        value=1,
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            html.Div(
                                className="three columns card",
                                children=[
                                    html.H6("Select a Date Range",),
                                    dcc.DatePickerRange(
                                        id="date-range-select",
                                        start_date=df['Entry time'].min(),
                                        end_date=df['Entry time'].max(),
                                        display_format='MMM YY' 
                                    )
                                ]
                            ),
                            html.Div(
                                id="strat-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-returns", className="indicator_value"),
                                    html.P('Strategy Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            html.Div(
                                id="market-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="market-returns", className="indicator_value"),
                                    html.P('Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            html.Div(
                                id="strat-vs-market-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-vs-market", className="indicator_value"),
                                    html.P('Strategy vs. Market Returns', className="twelve columns indicator_text"),
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                className="twelve columns card",
                children=[
                    dcc.Graph(
                        id="monthly-chart",
                        figure={
                            'data': []
                        }
                    )
                ]
            ),
            html.Div(
                className="padding row",
                children=[
                    html.Div(
                        className="six columns card",
                        children=[
                            dash_table.DataTable(
                                id='table',
                                columns=[
                                    {'name': 'Number', 'id': 'Number'},
                                    {'name': 'Trade type', 'id': 'Trade type'},
                                    {'name': 'Exposure', 'id': 'Exposure'},
                                    {'name': 'Entry balance', 'id': 'Entry balance'},
                                    {'name': 'Exit balance', 'id': 'Exit balance'},
                                    {'name': 'Pnl (incl fees)', 'id': 'Pnl (incl fees)'},
                                ],
                                style_cell={'width': '50px'},
                                style_table={
                                    'maxHeight': '450px',
                                    'overflowY': 'scroll'
                                },
                            )
                        ]
                    ),
                    dcc.Graph(
                        id="pnl-types",
                        className="six columns card",
                        figure={}
                    )
                ]
            ),
            html.Div(
                className="padding row",
                children=[
                    dcc.Graph(
                        id="daily-btc",
                        className="six columns card",
                        figure={}
                    ),
                    dcc.Graph(
                        id="balance",
                        className="six columns card",
                        figure={}
                    )
                ]
            )
        ]
    )        
])

@app.callback(
    dash.dependencies.Output('daily-btc', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_daily_btc(exchange_value, margin_value, start_date, end_date):
    tmp_df = filter_df(exchange_value, margin_value, start_date, end_date)

    return {
        'data': [go.Scatter(x=tmp_df['Entry time'], y=tmp_df['BTC Price'])],
        'layout': {
            'height': 400,
            'title': 'Daily BTC Price'
        }
    }

@app.callback(
    dash.dependencies.Output('balance', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_balance(exchange_value, margin_value, start_date, end_date):
    tmp_df = filter_df(exchange_value, margin_value, start_date, end_date)

    return {
        'data': [go.Scatter(x=tmp_df['Entry time'], y=tmp_df['Entry balance'])],
        'layout': {
            'height': 400,
            'title': 'Balance overtime'
        }
    }

@app.callback(
    dash.dependencies.Output('pnl-types', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_pnt_types(exchange_value, margin_value, start_date, end_date):
    tmp_df = filter_df(exchange_value, margin_value, start_date, end_date)

    data = []
    for name, group in tmp_df.groupby('Trade type'):
        grouped = group.groupby('Entry time date', as_index=False).mean()
        data.append(                                                                   
            go.Bar(x=grouped['Entry time date'], y=grouped['Pnl (incl fees)'], name=name)            
        )                                                                              

    return {
        'data': data,
        'layout': {
            'height': 400,
            'title': 'PnL vs Trade type'
        }
    }

@app.callback(
    [
        dash.dependencies.Output('date-range-select', 'start_date'),
        dash.dependencies.Output('date-range-select', 'end_date')
    ],
    [
        dash.dependencies.Input('exchange-select', 'value')
    ]
)
def update_dates_selector(value):
    tmpDf = df[df['Exchange'] == value]
    return tmpDf['Entry time'].min(), tmpDf['Entry time'].max()

def filter_df(exchange_value, margin_value, start_date, end_date):
    return df[df['Exchange'] == exchange_value] \
           [df['Margin'] == margin_value] \
           [df['Entry time'] >= start_date] \
           [df['Entry time'] <= end_date]

@app.callback(
    [
        dash.dependencies.Output('monthly-chart', 'figure'),
        dash.dependencies.Output('market-returns', 'children'),
        dash.dependencies.Output('strat-returns', 'children'),
        dash.dependencies.Output('strat-vs-market', 'children')
    ],
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_monthly_performance(exchange_value, margin_value, start_date, end_date):
    tmp_df = filter_df(exchange_value, margin_value, start_date, end_date)

    btc_returns = calc_btc_returns(tmp_df)
    strat_returns = calc_strat_returns(tmp_df)
    strat_vs_market = strat_returns - btc_returns

    return { 
        'data': monthly_performance_data(tmp_df),
        'layout': {
            'title': {
                'text': 'Overview of Monthly performance'
            }
        }
    }, f'{btc_returns:0.2f}%', f'{strat_returns:0.2f}%', f'{strat_vs_market:0.2f}%'

def monthly_performance_data(tmp_df):
    
    open_data  = tmp_df['Entry balance']
    high_data  = tmp_df['Entry balance']
    low_data   = tmp_df['Exit balance']
    close_data = tmp_df['Exit balance']
    dates      = tmp_df['year_month']
    
    return [go.Candlestick(x=dates,
                           open=open_data, high=high_data,
                           low=low_data, close=close_data)]

def calc_btc_returns(dff):
    btc_start_value = dff.tail(1)['BTC Price'].values[0]
    btc_end_value = dff.head(1)['BTC Price'].values[0]
    btc_returns = (btc_end_value * 100/ btc_start_value)-100
    return btc_returns

def calc_strat_returns(dff):
    start_value = dff.tail(1)['Exit balance'].values[0]
    end_value = dff.head(1)['Entry balance'].values[0]
    returns = (end_value * 100/ start_value)-100
    return returns

@app.callback(
    dash.dependencies.Output('table', 'data'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    )
)
def update_table(exchange_value, margin_value, start_date, end_date):
    dff = filter_df(exchange_value, margin_value, start_date, end_date)
    return dff.to_dict('records')

if __name__ == "__main__":
    app.run_server(debug=True)
