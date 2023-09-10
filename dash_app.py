# -*- coding: utf-8 -*-

'''
Created on 24 09. 2022

@author: Alex
'''
import base64
from dash import Dash

from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State

import io
from io import BytesIO

# import numpy as np
import pandas as pd

from dash_table.Format import Format, Scheme


import bio_df_processing as helper
import get_main_figure as gmf


app = Dash(__name__, 
           meta_tags=[{"name": "viewport", "content": "width=device-width"}])


# Colors
bgcolor = "#f3f3f1"  # mapbox light map land color
bar_bgcolor = "#b0bec5"  # material blue-gray 200
bar_unselected_color = "#78909c"  # material blue-gray 400
bar_color = "#546e7a"  # material blue-gray 600
bar_selected_color = "#37474f"  # material blue-gray 800
bar_unselected_opacity = 0.8

# Figure template
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}   



def patient_info(df):
    return html.Div(children=[
        html.H5('Информация о пациенте', style = {'fontSize' : 16, 'font-family' : 'sans-serif'}),
        dash_table.DataTable(
            columns=[{"name": str(i), "id": str(i)} for i in df.columns],
            data = df.to_dict('records'),
            style_header={
                'fontWeight': 'bold'
                },
            style_cell = {'textAlign': 'center','font-family':'sans-serif', 'fontSize':16},
            id = 'patient_info_table'
        )
    ])
    

def metabolit_info(df_in, name = 'Метаболиты'):
    """
    conditional formatting link
    https://dash.plotly.com/datatable/conditional-formatting
    """
    df = df_in.copy()
    df = df.dropna(subset=['Верхняя граница'])
    df['Метаболит'] = df.index.values
    cols = df.columns.to_list()
    df = df[[cols[-1]] + cols[:-1]]
    
    return html.Div(children=[
        html.H3(name,
                style={'text-align':'center','fontSize' : 20, 'font-family' : 'sans-serif'}),
        dash_table.DataTable(
            id = 'metabolit-table',
            columns=[{"name": str(i), "id": str(i), 
                      'type' :'numeric',
                      "format" : Format(precision=2, scheme=Scheme.fixed)} for i in df.columns],
            data = df.to_dict('records'),
            style_header={
                'fontWeight': 'bold',
                'textAlign': 'center'},
            style_cell={
                'textAlign': 'center',
                'fontSize':14, 
                'font-family':'sans-serif'
            },
            style_data_conditional=[                
                {
                    'if': {
                        'filter_query': '{Понижено} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'aqua',
                    'color': 'black'
                },
                {
                    'if': {
                        'filter_query': '{Риск понижения} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'aliceblue',
                    'color': 'black'
                },
                                {
                    'if': {
                        'filter_query': '{Риск повышения} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'lightyellow',
                    'color': 'black'
                },  
                {
                    'if': {
                        'filter_query': '{Повышено} > 0',
                        'column_id': 'Результат'
                    },
                    'backgroundColor': 'red',
                    'color': 'white'
                },                                                      
                
                ],
            style_table={
                'maxHeight': '600px',
                'minWidth': '98%', 'width': '98%', 'maxWidth': '98%',
                'overflowY' : 'auto'
                },
            fixed_columns={'headers': True, 'data': 1},
        ),
    ],
    className = "six columns pretty_container", style={'margin-left':'0px'})
     
    
    
def get_graph_color(value, b = 50):
    """
    value - in range 0-100
    """    
    r = int(255*value/100.)
    g = 255 - r
    return f'rgb({r},{g},{b})'

def models_output_cvd(deseases): 
    """ 
    deseases - dict: {'desease name' : desease probability} 
    """ 
    categories = list(deseases.keys())[::-1] 
    proba = list(deseases.values())[::-1] 
     
    colors = [] 
    labels = [] 
    for cat in categories: 
        colors.append(get_graph_color(deseases[cat])) 
        labels.append(f'<b>{deseases[cat]:.2f} %</b>') 
         
    fig = { 
        "data": [ 
            { 
                "type": "bar", 
                "x": proba, 
                "y": categories, 
                "marker": { 
                    "color": colors, 
                    }, 
                "text" : labels, 
                "textposition" : 'outside', 
                "insidetextanchor" : 'middle', 
                "hoverinfo": 'skip', 
             
                "orientation": "h", 
                "showlegend": False, 
            }, 
        ], 
        "layout": { 
            "template": template, 
            "barmode": "overlay", 
            "selectdirection": "v", 
            "height": 55, 
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10}, 
            "width" : "90%", 
            "xaxis": { 
                "range": [-1, 100], 
                "automargin": True, 
            }, 
            "yaxis": { 
                "type": "category", 
                "categoryorder": "array", 
                "categoryarray": categories, 
                "side": "left", 
                "automargin": True, 
            }, 
        }, 
    } 
    
    return dcc.Graph( 
            id='example-graph', 
            figure=fig, 
            config={ 
                'displayModeBar': False 
                } 
        )

def models_output(deseases): 
    """ 
    deseases - dict: {'desease name' : desease probability} 
    """ 
    categories = list(deseases.keys())[::-1] 
    proba = list(deseases.values())[::-1] 
     
    colors = [] 
    labels = [] 
    for cat in categories: 
        colors.append(get_graph_color(deseases[cat])) 
        labels.append(f'<b>{deseases[cat]:.2f} %</b>') 
         
    fig = { 
        "data": [ 
            { 
                "type": "bar", 
                "x": proba, 
                "y": categories, 
                "marker": { 
                    "color": colors, 
                    }, 
                "text" : labels, 
                "textposition" : 'outside', 
                "insidetextanchor" : 'middle', 
                "hoverinfo": 'skip', 
             
                "orientation": "h", 
                "showlegend": False, 
            }, 
        ], 
        "layout": { 
            "template": template, 
            "barmode": "overlay", 
            "selectdirection": "v", 
            "height": 120, 
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10}, 
            "width" : "90%", 
            "xaxis": { 
                "range": [-1, 100], 
                "automargin": True, 
            }, 
            "yaxis": { 
                "type": "category", 
                "categoryorder": "array", 
                "categoryarray": categories, 
                "side": "left", 
                "automargin": True, 
            }, 
        }, 
    }     
     
    return  dcc.Graph( 
            id='example-graph', 
            figure=fig, 
            config={ 
                'displayModeBar': False 
                }, style = {'margin-top':'10px'}  )
   

def main_figure():
    fig = gmf.get_plot()
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return html.Div(children = html.Div([
        html.Img(src="data:image/png;base64,{}".format(fig_data), sizes="100%100%",
                    style={'width':'100%','border-radius':'5px 5px 0px 0px', 'margin-top':'8px', 'margin-bottom':'-10px'}),
        html.Img(src = 'assets/legend_full.png', style={'width':'100%','border-radius':'0px 0px 5px 5px'})]))




#LC part introduction
def models_output_lc(deseases):
    """
    deseases - dict: {'desease name' : desease probability}
    """
    categories = list(deseases.keys())[::-1]
    proba = list(deseases.values())[::-1]
    
    colors = []
    labels = []
    for cat in categories:
        colors.append(get_graph_color(deseases[cat]))
        labels.append(f'<b>{deseases[cat]:.2f} %</b>')
        
    fig = {
        "data": [
            {
                "type": "bar",
                "x": proba,
                "y": categories,
                "marker": {
                    "color": colors,
                    },
                "text" : labels,
                "textposition" : 'outside',
                "insidetextanchor" : 'middle',
                "hoverinfo": 'skip',
            
                "orientation": "h",
                "showlegend": False,
            },
        ],
        "layout": {
            "template": template,
            "barmode": "overlay",
            "selectdirection": "v",
            "height": 150,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 2},
            "width" : "90%",
            "xaxis": {
                "range": [-1, 100],
                "automargin": True,
            },
            "yaxis": {
                "type": "category",
                "categoryorder": "array",
                "categoryarray": categories,
                "side": "left",
                "automargin": True,
            },
        },
    }    
    
    return html.Div(children = [
        html.H3('Онкологические заболевания',
                style={'text-align':'center','fontSize' : 20, 'font-family' : 'sans-serif'}),
        dcc.Graph(
            id='example-graph',
            figure=fig,
            config={
                'displayModeBar': False
                }
        ),html.Br(),
        
        ],
        className="six columns pretty_container", style={'margin-left':'0px'})



app.layout = html.Div(children=[
    html.Div([html.Div([html.Img(src ='assets/NCMU_logo.jpeg',
                             style={'width':'100px','height':'110px'}),
                       html.Img(src ='assets/sechenov_logo(1).png',
                             style={'width':'110px', 'height':'110px', 'margin-left':'16px'})],style={'width':'50%','display':'inline-block'}),
                      html.Div([
                          html.Img(src ='assets/metaboscan_logo.png',
                                 style={'float':'right','width':'200px','margin-top':'25px'})],
                          style={'width':'50%','display':'inline-block'}),],
                        style={'width':'100%','display':'flex','margin-top':'10px'}),
    html.H1(children='Скрининговая система диагностики патологий', style = {'textAlign': 'center', 'color' : '#000036',
                                                                            'fontSize' : 33,'margin-top':'10px',
                                                                            'margin-bottom':'10px', 'border-radius':'5px',
                                                                            'margin-left':'0px'},
            className = "six columns pretty_container"),
    html.Div(children=[html.Div('''
        Загрузите файл с результатами метаболомного профиля
    ''', style = {'margin-left':'10px'}),
        dcc.Upload(
            id='upload-data',
            children=html.Div(
                'Загрузите данные',
            style={
                'cursor':'pointer',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'background':  'whitesmoke',
                'padding': '0px',
            }),
            # Allow multiple files to be uploaded
            multiple=True
        )],
        # # className = 'inputPart'
        className = "six columns pretty_container", style={'border-radius':'0px 0px 5px 5px','margin-left':'0px'}
    ),
    html.Br(),

    html.Div(children = [],
             id = 'output-data-upload',
             # className = "six columns pretty_container"
             ),
    ],
    
    className = 'page'
    )



def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_excel(io.BytesIO(decoded))  
        # df = pd.read_excel('C:\\Users\\MATH\\bio\\TEST_test.xlsx')
            
        info, profile, groups_content = helper.prepare_data(df)
        
        desease_cvd = helper.desease_prediction_cvd(profile)
        desease = helper.desease_prediction(profile)
        desease_lc=helper.desease_prediction_lc(profile)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ], className="six columns pretty_container", style={'margin-left':'0px'})

    
    meta_tables = []
    for name, values in groups_content.items():
        meta_tables.append(metabolit_info(profile.loc[values], name=name))
    return html.Div([html.Div([
            html.Div([ 
                    html.H3(children='Результаты метаболомного профилирования',
                            style = {'textAlign': 'center', 'font-family' : "sans-serif"
                                }),
                    html.Br(),         
                
                    patient_info(info),
                    ],
                className="six columns pretty_container", style={'margin-left':'0px'}
                ),
            main_figure(),
            
            html.Div(children = [ 
        html.H3('Сердечно-сосудистые патологии', 
                style={'text-align':'center','fontSize' : 20, 'font-family' : 'sans-serif'}), 
        models_output_cvd(desease_cvd),
        models_output(desease)],
        className="six columns pretty_container", style={'margin-left':'0px'},),

            models_output_lc(desease_lc)
            ]  + meta_tables,),
            html.Div([html.Div(html.P(children='Результаты данного отчета не являются диагнозом и должны быть интерпретированы лечащим врачом на основании клинико-лабораторных данных и других диагностических исследований',
                             style={'textAlign':'left','font-style':'italic','font-size':'13px','margin-top':'4px'}),style={'width':'52%','display':'inline-block'}),
                      html.Div([
                          html.P(children='117418 Москва | Нахимовский проспект, 45',
                                 style={'textAlign':'right','font-size':'11px','margin':'0px'}),

                          html.P(children='Лаборатория фармакокинетики и метаболомного анализа',
                                 style={'textAlign':'right','font-weight':'bold','font-size':'11px','margin':'0px'}),

                          html.P(children='Институт трансляционной медицины и биотехнологий',
                                 style={'textAlign':'right','font-size':'11px','margin':'0px'}),

                          html.P(children='Сеченовского Университета',
                                 style={'textAlign':'right','font-size':'11px','margin':'0px'})],
                          style={'width':'48%','display':'inline-block'}),],
                        style={'width':'100%','display':'flex','margin-top':'10px'}),])


 


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              )
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children




# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)