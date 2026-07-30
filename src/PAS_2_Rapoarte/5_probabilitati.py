import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px

CATEGORII = ('spalat', 'vase', 'uscator')
PRAGURI_PORNIT = {'spalat': 100, 'uscator': 60, 'vase': 60}

PERIOADE = ['noapte', 'dimineata', 'pranz', 'seara']
TIPURI_ZI = ['zi lucratoare', 'weekend']
ANOTIMPURI = ['iarna', 'primavara', 'vara', 'toamna']

LUNA_ANOTIMP = {12: 'iarna', 1: 'iarna', 2: 'iarna',
                3: 'primavara', 4: 'primavara', 5: 'primavara',
                6: 'vara', 7: 'vara', 8: 'vara',
                9: 'toamna', 10: 'toamna', 11: 'toamna'}

LIMITE_PERIOADE = [-1, 5, 11, 17, 23]

CHEI = ['casa', 'categorie', 'anotimp', 'tip_zi', 'perioada_zi']
CONTEXT = ['casa', 'categorie', 'anotimp', 'tip_zi']

CASA_ALEASA = 'casa_2000904'


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
    SELECT categorie, consum, timp_consum, hour, dayofweek, month
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
df_consum['tip_zi'] = df_consum['dayofweek'].apply(tip_zi)
df_consum['anotimp'] = df_consum['month'].map(LUNA_ANOTIMP)
df_consum['perioada_zi'] = pd.cut(df_consum['hour'], bins=LIMITE_PERIOADE, labels=PERIOADE)
#print(df_consum)

df_activ = df_consum[df_consum['activ']]

zile_active = df_activ.groupby(CHEI, observed=True)['zi'].nunique().rename('zile_active')
zile_totale = df_consum.groupby(CONTEXT, observed=True)['zi'].nunique().rename('zile_totale')

# combinatiile fara nicio utilizare lipsesc dupa groupby, deci le construim explicit
df_dimensiuni = pd.MultiIndex.from_product(
    [ANOTIMPURI, TIPURI_ZI, PERIOADE],
    names=['anotimp', 'tip_zi', 'perioada_zi']).to_frame(index=False)

df_perechi = df_consum[['casa', 'categorie']].drop_duplicates()
df_grila = df_perechi.merge(df_dimensiuni, how='cross')

df_probabilitati = (df_grila
                    .merge(zile_active.reset_index(), on=CHEI, how='left')
                    .merge(zile_totale.reset_index(), on=CONTEXT, how='left'))
df_probabilitati['zile_active'] = df_probabilitati['zile_active'].fillna(0)
df_probabilitati = df_probabilitati.dropna(subset=['zile_totale'])

df_probabilitati['probabilitate'] = (df_probabilitati['zile_active'] / df_probabilitati['zile_totale']).round(3)

print(df_probabilitati.pivot_table(index='perioada_zi', columns=['categorie', 'tip_zi'],
                                   values='probabilitate')
      .reindex(PERIOADE).round(3).to_string())

df_grafic = df_probabilitati[(df_probabilitati['casa'] == CASA_ALEASA) &
                             (df_probabilitati['categorie'] == 'uscator')]

px.bar(df_grafic, x='perioada_zi', y='probabilitate', color='anotimp',
       facet_col='tip_zi', barmode='group', height=600,
       category_orders={'perioada_zi': PERIOADE, 'anotimp': ANOTIMPURI,
                        'tip_zi': TIPURI_ZI},
       labels={'perioada_zi': 'Perioada zilei', 'probabilitate': 'P(activ)',
               'anotimp': 'Anotimp'}).show()
