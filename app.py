import dash
import dash_table
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# read file
df = pd.read_csv('data/indicators.csv')

# get unique attributes for selection
available_indicators = df['Indicator Name'].unique()

app = dash.Dash(__name__)
app.title = "World statistics"
server = app.server
app.layout = html.Div(id = 'container', children = [

    html.Div(id = 'header', children = [
        html.H1('World statistics',
                id = 'title'
                )
    ]),

    html.Div(id = 'content', children=[
        html.Div(id = 'country_div', children = [
            dcc.Dropdown(
                id = 'country',
                options = [{'label': s, 'value': s} for s in df['Country Name'].unique()],
                value = [],
                placeholder = 'Select category or country',
                multi = True,
                className = 'dropdown'
            )
        ]),
        html.Div(id = 'left', children = [
            dcc.Dropdown(
                id = 'xaxis_dropdown',
                options = [{'label': s, 'value': s} for s in available_indicators],
                placeholder = 'Select x-axis attribute',
                className = 'dropdown'
            ),
            dcc.RadioItems(
                id = 'radio_left',
                options = [{'label': s, 'value': s} for s in ['Linear', 'Log']],
                value = 'Linear',
                className = 'radio'
            )
        ]),
        html.Div(id = 'right', children = [
            dcc.Dropdown(
                id = 'yaxis_dropdown',
                options = [{'label': s, 'value': s} for s in available_indicators],
                placeholder = 'Select y-axis attribute',
                className = 'dropdown'
            ),
            dcc.RadioItems(
                id = 'radio_right',
                options = [{'label': s, 'value': s} for s in ['Linear', 'Log']],
                value = 'Linear',
                className = 'radio'
            )
        ]),
        dcc.Graph(id = 'graph'),
        dcc.Slider(
            id = 'slider',
            min = df.Year.min(),
            max = df.Year.max(),
            step = 5,
            marks = {str(i): str(i) for i in df['Year'].unique()},
            value = df.Year.max(),
            className = 'slider'
        ),
        html.Br(),
        html.Div(
            id = 'data_table_div'
        )
    ])
])


# create graph depending on following parameters:
# x-value, y-value, year, linear/logarithmic scale (for each axis), country
@app.callback(Output('graph', 'figure'),
              [Input('xaxis_dropdown', 'value'),
               Input('yaxis_dropdown', 'value'),
               Input('slider', 'value'),
               Input('radio_left', 'value'),
               Input('radio_right', 'value'),
               Input('country', 'value')])
def update_graph(xaxis_value, yaxis_value, year, radio_left, radio_right, country_value):

    # create separate dataframes
    selected_data = df[(df['Year'] == year) & (df['Country Name'].isin(country_value))]
    rest_data = df[(df['Year'] == year) & (df['Country Name'].isin(country_value) == False)]

    # create scatter plot for each dataframe
    data = [go.Scatter(
        x = i[i['Indicator Name'] == xaxis_value]['Value'],
        y = i[i['Indicator Name'] == yaxis_value]['Value'],
        name = '',
        text = i[i['Indicator Name'] == yaxis_value]['Country Name'],
        mode = 'markers',
        marker = {
            'size':15,
            'line': {'width': 0.2, 'color': 'white'},
            'color': '#0878db' if i is rest_data else '#db0808'
        }
        ) for i in [rest_data, selected_data]
    ]

    layout = go.Layout(
        xaxis = dict(title = xaxis_value, type = 'linear' if radio_left == 'Linear' else 'log'),
        yaxis = dict(title= yaxis_value, type='linear' if radio_right == 'Linear' else 'log'),
        hovermode = 'closest',
        showlegend = False
    )

    # return data and layout elements to graph
    return {'data': data, 'layout': layout}


@app.callback(output = Output('data_table_div', 'children'),
              inputs = [Input('country', 'value'),
                        Input('slider', 'value')])
def create_data_table(country_value, year):
    if len(country_value) < 1:
        return

    selected_data = df[(df['Year'] == year) & (df['Country Name'].isin(country_value))]

    return dash_table.DataTable(
        id = 'DataTable',
        columns = [{'name': i, 'id': i} for i in df.columns],
        data = selected_data.to_dict('records'),
        sort_action = 'native',
        filter_action = 'native',
        export_format='xlsx',
        export_headers='display'
        )

if __name__ == '__main__':
    app.run_server()
