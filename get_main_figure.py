import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import base64
from dash import Dash

import io
from io import BytesIO

from dash import dcc
from dash import html
from dash import dash_table

from bio_df_processing import prepare_data, add_all_ranges,\
extract_info

df = pd.read_excel("TEST_test.xlsx")

toxic=['Kynurenine', 'Kynurenine/Tryptophan', 'Quinolinic acid','Antranillic acid', 'Xanturenic acid', 
       'Kynurenic acid', 'Tryptophan','Kynurenine/Tryptophan','АДМА',
       'СДМА', 'АДМА/Аргинин']
microbiota=['Indole-3-lactate', 'Indole-3-acetate', 'Indole-3-carboxaldehyde', 'Indole-3-acrylate',
       'Indole-3-propionate', 'Indole-3-butyrate', 'Tryptamine']
stress=['HIAA','Serotonin', 'Холин (свободный)']
aminoacids=['Глицин', 'Аланин', 'Пролин', 'Валин', 'Лейцин', 'Изолейцин', 'Орнитин',
       'Аспаргиновая кислота', 'Фенилаланин', 'Аргинин', 'Цитруллин', 'Серин',
       'Треонин', 'Лизин', 'Тирозин', 'Метионин']
groups2=[toxic, microbiota, stress, aminoacids]
names=['Окислительный стресс', 'Микробные метаболиты', 'Стресс &\nнастроение', 'Профиль\nаминокислот']
diseases=['Преждевременное\nстарение организма','Сердечно-сосудистые\nзаболевания', 'Рак легкого', 'Рак почки', 'Колоректальный рак']

proba_age = 48.0
proba_CVD = 78.0
proba_lung = 5.0
proba_kidney = 4.0
proba_colorectal = 2.0

y_line=[-0.5,0.8,1.8,2.8]
y_line_2=[5,7.5,9,10.5,12.0]
numbers=[8,7,6,5]
numbers_dis=[5,4,3,2,1]

def process_data(df):
    info = extract_info(df)
    df = df.drop(info.columns, axis = 1)
    df = df.T
    df.columns = ['Результат']
    df.index = df.index.str.strip()
    df_0 = add_all_ranges(df)

    df_selected=df_0.loc[df_0['Результат'] > df_0['Верхняя граница']]
    df_selected_1=df_0.loc[df_0['Результат'] < df_0['Нижняя граница']]
    a=df_selected.T.columns
    a=a.append(df_selected_1.T.columns)
    return a

part=[]
for group in groups2:    
    prop=set(process_data(df).intersection(group))
    percentage=round(len(prop)/len(group)*100, 0)
    part.append(percentage)
    part_dis=[proba_age, proba_CVD, proba_lung, proba_kidney, proba_colorectal]

def get_plot():
    plt.figure(figsize=(7,5))
    plt.plot(part, y_line, 'ro', marker='o', markersize=0)
    plt.hlines(y=14.5, xmin=60, xmax=100, linewidth=10, color='r')
    plt.hlines(y=14.5, xmin=20, xmax=60, linewidth=10, color='gold')
    plt.hlines(y=14.5, xmin=0, xmax=20, linewidth=10, color='seagreen')
    plt.hlines(y=4.3, xmin=0, xmax=100, linewidth=3, color='lightgrey')
    plt.hlines(y=6.8, xmin=0, xmax=100, linewidth=3, color='lightgrey')

    plt.rcParams['font.family'] = 'serif'
    plt.grid(True, linewidth=0.15, color = 'Grey')
    plt.yticks(c='white')
    plt.xticks(size=7, c='b')
    n=0
    for i_x, i_y in zip(part, y_line):
        plt.xlim(0,100)
        plt.ylim(-1,15)
        number = dict(boxstyle='circle', facecolor='grey', alpha=0.07, edgecolor='black')
        if i_x < 20.0:
            prop = dict(boxstyle='round', facecolor='lightgreen', alpha=1, edgecolor='g')
            
        elif i_x > 60.0:    
            prop = dict(boxstyle='round', facecolor='tomato', alpha=1, edgecolor='r')
        else:
            prop = dict(boxstyle='round', facecolor='lemonchiffon', alpha=1, edgecolor='sienna')
        plt.text(i_x-4, i_y+0.2, names[n], color = 'black',  bbox=prop, fontsize = 8)
        plt.text(i_x, i_y-0.4, numbers[n], color = 'black',  bbox=number, fontsize = 7)
        n=n+1

    n=0
    for i_x, i_y in zip(part_dis, y_line_2):
        plt.xlim(0,100)
        plt.ylim(-1,16)
        number = dict(boxstyle='circle', facecolor='black', alpha=0.07, edgecolor='black')
        if i_x < 20.0:
            prop = dict(boxstyle='round', facecolor='lightgreen', alpha=1, edgecolor='g')
            
        elif i_x > 60.0:    
            prop = dict(boxstyle='round', facecolor='lightsalmon', alpha=1, edgecolor='r')
        else:
            prop = dict(boxstyle='round', facecolor='lemonchiffon', alpha=1, edgecolor='sienna')
        plt.text(i_x-1, i_y+0.3, diseases[n], color = 'black',  bbox=prop, fontsize = 8)
        plt.text(i_x, i_y-0.4, numbers_dis[n], color = 'black',  bbox=number, fontsize = 8)
        n=n+1
        
    plt.text(40, 15, 'Степень риска', color = 'black', fontsize = 10)
    plt.text(2, 13.5, 'минимальная', fontsize = 9)
    plt.text(34, 13.5, 'средняя', fontsize = 9)
    plt.text(80, 13.5, 'высокая', fontsize = 9)
    for pos in ['top']:
        plt.gca().spines[pos].set_visible(False)
    
    fig = plt.Figure()
    fig.set_canvas(plt.gcf().canvas)
    return  plt

def save_figure():
    fig = get_plot()
    # Save it to a temporary buffer.
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    fig.close()
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("utf8")
    buf.close()
    fig_main_matplotlib = f'bio-master:main_png;base64,{fig_data}'
    return fig_main_matplotlib

get_plot()