import sqlite3

import pandas as pd
import plotly.express as px

CATEGORII = ('spalat', 'vase', 'uscator')

# pragul jos delimiteaza capetele ciclului, pragul sus confirma ca a fost o utilizare reala
PRAG_JOS = 5
PRAGURI_PORNIT = {'spalat': 100, 'uscator': 60, 'vase': 60}

PAS_MINUTE = 10
DURATA_MINIMA = 40

PERIOADE = ['noapte', 'dimineata', 'pranz', 'seara']
LIMITE_PERIOADE = [-1, 5, 11, 17, 23]

LUNA_ANOTIMP = {12: 'iarna', 1: 'iarna', 2: 'iarna',
                3: 'primavara', 4: 'primavara', 5: 'primavara',
                6: 'vara', 7: 'vara', 8: 'vara',
                9: 'toamna', 10: 'toamna', 11: 'toamna'}

CASA_ALEASA = 'casa_2000901'


def tip_zi(dayofweek):
    return 'weekend' if dayofweek >= 5 else 'zi lucratoare'


def mediana_kwh(energie_wh):
    return round(energie_wh.median() / 1000, 2)


def cicluri_aparat(df_aparat, prag_sus):
    # un ciclu e o secventa neintrerupta de masuratori peste pragul jos
    df = df_aparat.sort_values('timp_consum')

    pornit = df['consum'] > PRAG_JOS
    # o pauza in inregistrare nu trebuie sa lipeasca doua cicluri diferite
    intrerupt = df['timp_consum'].diff() > pd.Timedelta(minutes=PAS_MINUTE)
    grup = ((pornit != pornit.shift()) | intrerupt).cumsum()

    if not pornit.any():
        return pd.DataFrame()

    df_cicluri = (df[pornit]
                  .groupby(grup[pornit])
                  .agg(start=('timp_consum', 'min'),
                       sfarsit=('timp_consum', 'max'),
                       energie_wh=('consum', 'sum'),
                       varf=('consum', 'max'),
                       n_masuratori=('consum', 'size'))
                  .reset_index(drop=True))

    df_cicluri['durata_min'] = df_cicluri['n_masuratori'] * PAS_MINUTE

    # grupurile care n-au atins niciodata pragul sus nu sunt utilizari reale
    return df_cicluri[df_cicluri['varf'] > prag_sus]


conn = sqlite3.connect('./data/case/case_curate.sqlite3')

query = """
SELECT name
FROM sqlite_master
WHERE type='table'
"""
tabele = pd.read_sql_query(query, conn)['name'].tolist()

toate = []
zile_casa = {}
for nume_tabel in tabele:
    query = f"""
    SELECT id_appliance, Name, categorie, consum, timp_consum
    FROM "{nume_tabel}"
    WHERE categorie IN {CATEGORII}
    """
    df_casa = pd.read_sql_query(query, conn, parse_dates=['timp_consum'])
    if df_casa.empty:
        continue

    zile_casa[nume_tabel] = df_casa['timp_consum'].dt.normalize().nunique()

    # fiecare aparat se grupeaza separat, altfel ultimul ciclu al unuia
    # se lipeste de primul ciclu al urmatorului
    for (id_aparat, categorie), df_aparat in df_casa.groupby(['id_appliance', 'categorie']):
        df_aparat_cicluri = cicluri_aparat(df_aparat, PRAGURI_PORNIT[categorie])
        if df_aparat_cicluri.empty:
            continue
        df_aparat_cicluri.insert(0, 'casa', nume_tabel)
        df_aparat_cicluri.insert(1, 'id_appliance', id_aparat)
        df_aparat_cicluri.insert(2, 'categorie', categorie)
        toate.append(df_aparat_cicluri)

conn.close()

df_cicluri = pd.concat(toate, ignore_index=True)

df_cicluri['zi'] = df_cicluri['start'].dt.strftime('%Y-%m-%d')
df_cicluri['ora_start'] = df_cicluri['start'].dt.hour
df_cicluri['tip_zi'] = df_cicluri['start'].dt.dayofweek.apply(tip_zi)
df_cicluri['anotimp'] = df_cicluri['start'].dt.month.map(LUNA_ANOTIMP)
df_cicluri['perioada_zi'] = pd.cut(df_cicluri['ora_start'],
                                   bins=LIMITE_PERIOADE, labels=PERIOADE).astype(str)
df_cicluri['saptamana'] = df_cicluri['start'].dt.isocalendar().week.astype(int)

# ciclurile foarte scurte sunt de obicei taiate la capetele inregistrarii;
# le marcam, nu le stergem, ca sa se vada cate sunt
df_cicluri['prea_scurt'] = df_cicluri['durata_min'] < DURATA_MINIMA

conn = sqlite3.connect('./data/case/cicluri.sqlite3')
df_cicluri.to_sql('cicluri', conn, if_exists='replace', index=False)
conn.close()


df_grafic = df_cicluri[df_cicluri['casa'] == CASA_ALEASA]

px.histogram(df_grafic, x='durata_min', facet_row='categorie', nbins=40, height=700, color = 'categorie',
             category_orders={'categorie': ['spalat', 'uscator', 'vase']},
             labels={'durata_min': 'Durata ciclului [min]', 'count': 'Numar cicluri'},
             title=f'Distributia duratei ciclurilor - {CASA_ALEASA}').show()
