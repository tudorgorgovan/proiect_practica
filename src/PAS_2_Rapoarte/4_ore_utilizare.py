import sqlite3
from itertools import product

import pandas as pd
import plotly.express as px

CATEGORII = ('spalat', 'vase', 'uscator')
PRAGURI_PORNIT = {'spalat': 100, 'uscator': 60, 'vase': 60}

ORE = list(range(24))

TIPURI_ZI = ['zi lucratoare', 'weekend']


def tip_zi(dayofweek):
    return 'weekend' if dayofweek >= 5 else 'zi lucratoare'


conn = sqlite3.connect('./data/case/case_curate.sqlite3')

query = """
SELECT name
FROM sqlite_master
WHERE type='table'
"""
tabele = pd.read_sql_query(query, conn)['name'].tolist()

toate = []
for nume_tabel in tabele:
    query = f"""
    SELECT categorie, consum, timp_consum, hour, dayofweek
    FROM "{nume_tabel}"
    WHERE categorie IN {CATEGORII}
    """
    df_casa = pd.read_sql_query(query, conn)
    df_casa.insert(0, 'casa', nume_tabel)
    toate.append(df_casa)

conn.close()

df_consum = pd.concat(toate, ignore_index=True)
df_consum['prag'] = df_consum['categorie'].map(PRAGURI_PORNIT)
df_consum['activ'] = df_consum['consum'] > df_consum['prag']
df_consum['zi'] = df_consum['timp_consum'].str[:10]
df_consum['casa_zi'] = df_consum['casa'] + '|' + df_consum['zi']
df_consum['tip_zi'] = df_consum['dayofweek'].apply(tip_zi)


df_activ = df_consum[df_consum['activ']]

zile_active = df_activ.groupby(['categorie', 'tip_zi', 'hour'])['casa_zi'].nunique().rename('zile_active')
zile_totale = df_consum.groupby(['categorie', 'tip_zi'])['casa_zi'].nunique().rename('zile_totale')

grila = pd.DataFrame(
    list(product(sorted(df_consum['categorie'].unique()), TIPURI_ZI, ORE)),
    columns=['categorie', 'tip_zi', 'hour'])

df_probabilitati = (grila
                    .merge(zile_active.reset_index(), on=['categorie', 'tip_zi', 'hour'], how='left')
                    .merge(zile_totale.reset_index(), on=['categorie', 'tip_zi']))
df_probabilitati['zile_active'] = df_probabilitati['zile_active'].fillna(0)

df_probabilitati['probabilitate'] = (100 * df_probabilitati['zile_active'] / df_probabilitati['zile_totale']).round(1)

print(df_probabilitati.pivot_table(index='hour', columns=['categorie', 'tip_zi'],values='probabilitate').to_string())

px.bar(
    df_probabilitati,
    x='hour',
    y='probabilitate',
    color='tip_zi',
    facet_row='categorie',
    barmode='group',
    height=900,
    category_orders={'categorie': ['spalat', 'uscator', 'vase'],
                     'tip_zi': TIPURI_ZI},
    labels={'hour': 'Ora zilei', 'probabilitate': 'P(activ) [%]', 'tip_zi': 'Tip zi'},
    title='Probabilitatea de functionare: zi lucratoare vs weekend',
).update_xaxes(dtick=1).show()
