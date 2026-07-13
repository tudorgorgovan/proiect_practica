import sqlite3
import pandas as pd
import plotly.express as px
import os


def modificare_nume(nume):
    for caracter in '\\/*?:"<>|':
        nume = nume.replace(caracter, '_')
    return nume


conn = sqlite3.connect('./data/case/case.sqlite3')
cursor = conn.cursor()
query = """
SELECT
    name
FROM sqlite_master
WHERE type='table';
"""

cursor.execute(query)
tabele = cursor.fetchall()


for table_name in tabele:
    nume_tabel_sursa = table_name[0]
    query_select = f'SELECT * FROM "{nume_tabel_sursa}";'
    df = pd.read_sql_query(query_select, conn)

    nr_appliance = df['id_appliance'].unique()

    nume_consumatori = []
    for id_appliance in nr_appliance:
        rand_appliance = df[df['id_appliance'] == id_appliance]
        nume = rand_appliance['Name'].iloc[0]
        nume_consumatori.append(nume)

    fig = px.line(
        df,
        x='timp_consum',
        y='consum',
        color='Name',
        category_orders={'Name': nume_consumatori},
    )

    for idx, trace in enumerate(fig.data):
        trace.visible = (idx == 0)

    optiuni_selectie = []
    for idx, nume_appliance in enumerate(nume_consumatori):
        vizibilitate = [False] * len(nume_consumatori)
        vizibilitate[idx] = True
        optiuni_selectie.append(dict(
            label=nume_appliance,
            method='update',
            args=[
                {'visible': vizibilitate},
                {'title.text': nume_appliance},
            ],
        ))
    fig.update_layout(
        title=dict(
            text=nume_consumatori[0] if nume_consumatori else nume_tabel_sursa,
            x=0.5,
            xanchor='center',
            y=0.95,
            yanchor='top',
        ),
        xaxis_title='Timestamp',
        yaxis_title='Consum',
        showlegend=False,
        margin=dict(t=100),
        updatemenus=[dict(
            type='dropdown',
            active=0,
            buttons=optiuni_selectie,
            x=0,
            xanchor='left',
            y=1.15,
            yanchor='top',
        )],
    )


    fig.write_html(os.path.join('./grafice', f'{modificare_nume(nume_tabel_sursa)}.html'))

conn.close()