import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import plotly.figure_factory as ff



df = pd.read_csv('https://raw.githubusercontent.com/figela/data_viz/master/condu.csv',encoding='latin1', delimiter=';')
df.catv = df.catv.astype("category")
df.atm = df.atm.astype("category")
tpe_catv = set(df.catv)
tpe_atm = set(df.atm)

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets)

server = app.server

app.config["suppress_callback_exceptions"] = True


app.layout = html.Div(
    id="whole-container",
    children=[
        # header
     html.Div(
            [
                html.Span("Dashboard Accidents",
                style={'color':'#31a2ee',
                        'font-size':'3rem',
                        'letter-spacing':'-.1rem',
                        'vertical-align':'middle'}),

                html.Div(id="hidden-div", style={"display": "none"}),
              
            ],
        
            style={"margin":"0px",
                "background-color":"#b9b5b0",
                "height":"70px",
                "color":"blue",
                "padding-right":"2%",
                "padding-left":"2%"}
        ),
        # graph
        html.Div(
            [
                html.Div(
                    [
                        # Graphe
                        dcc.Graph(id="graph")
                    ],
                    className="seven columns",
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="dropdown-dis",
                            options=[{"label": s, "value": s} for s in tpe_catv],
                            value=list(tpe_catv),
                            multi=True,
                            style = {'width':'500px'}
                        )
                    ],
                    className=("three columns"),
                    style={
                        "color": "DodgerBlue",
                        "padding": "0px 5px",
                        "display": "",
                        "margin-right": "1px",
                        "margin-left": "50px",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(id='my-distri',
                        style={'width':'400px'})
                        
                    ],
                    className='four columns',
                    style={'width':'500'}
                ),
            ],
            style={"padding": "10px 0px 10px 0px", "display": ""},
        ),
        html.Div(
            [
                dcc.RangeSlider(
                    id="hour-slider",
                    count=1,
                    min=0,
                    max=24,
                    step=1,
                    value=[0, 24],
                    marks={i: "Hour {}".format(i) for i in [0, 6, 12, 18, 24]},
                    className="seven columns",
                )
            ]
        ),
        html.Div(
            [
                dcc.Checklist(id='my-check',
                    options=[
                        {'label': 'Male', 'value': 'Masculin'},
                        {'label': 'Female', 'value': 'Autre'}
                    ],
                    value=['Masculin', 'Autre'],
                    labelStyle={'display': 'inline-block','color':'dodgerblue'}
                )
            ],className="two columns",
            style={'margin-top' : '0px',
                'margin-right' : '1700px'}
            
        )
    ],
)



@app.callback(
    dash.dependencies.Output("graph", "figure"),
    [dash.dependencies.Input("hour-slider", "value"),
    dash.dependencies.Input("my-check", "value")],
)
def update_graph(hour_slider, my_check):
    h1 = hour_slider
    hour_slider = [int(str(x) + "00") for x in hour_slider]
    
    dff=df
    if my_check == ['Masculin']:
        dff = df[df['sexe']=='Masculin']
    elif my_check==['Autre']:
        dff = dff[dff['sexe']=='Autre']
    
    df_bar_col = dff[(dff["hrmn"] >= hour_slider[0]) & (dff["hrmn"] <= hour_slider[1])]
    b = df_bar_col.groupby(["catv", "atm"]).sum()
    l = b.columns.tolist()
    l.remove("catu")
    b = b.drop(columns=l)
    c = pd.DataFrame(index=list(tpe_atm), columns=list(tpe_catv))
    for el in tpe_catv:
        c[el] = b.transpose()[el].transpose()
    df_bar_col = c    
    figure = dict(
        data=[
            go.Bar(x=df_bar_col.index, y=df_bar_col.Quad, name="Quad"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Scooter, name="Scooter"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Motocyclette, name="Motocyclette"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Voiture, name="Voiture"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Autocar, name="Autocar"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Bicyclette, name="Bicyclette"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Autobus, name="Autobus"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Tramway, name="Tramway"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Autres, name="Autres"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.PL, name="PL"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Train, name="Train"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Tracteur, name="Tracteur"),
            go.Bar(x=df_bar_col.index, y=df_bar_col.Cyclomoteur, name="Cyclomoteur"),
        ],
        layout=dict(
            barmode="stack",
            xaxis={"categoryorder": "total descending"},
            yaxis={"categoryorder": "total ascending"},
            title="Accidents between {}-{} o'clock".format(h1[0], h1[1]),
        ),
    )

    return figure


@app.callback(
    Output('my-distri', 'figure'),
    [Input('dropdown-dis', 'value')])

def update_distri(value):
    
    if value == []:
        return {}
    df_distri = df.mask(~df.catv.isin(value)).dropna(inplace=False)
    figure = ff.create_distplot([df_distri['hrmn']], ['Accidents density'], colors=['coral'],
                         bin_size=80, show_rug=False)
    figure.update_layout(title_text='Accidents distribution',
                    plot_bgcolor='white',
                    showlegend=False,
                     xaxis = dict(
                        tickmode = 'array',
                        tickvals = [600, 1200, 1800, 2400],
                        ticktext = ['6am', '12am', '6pm', '12pm']))
    return figure

if __name__ == "__main__":
    app.run_server(debug=True)
