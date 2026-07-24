import sqlite3
import pandas as pd

CONTROLABIL = {
    'frigider': False,
    'spalat': True,
    'vase': True,
    'uscator': True,
    'boiler_el': True,
    'incalzire': True,
    'plita': False,
    'cuptor': False,
    'microunde': False,
    'tv': False,
    'lampa': False,
    'pompa_boiler': False,
    'total_light': False,
    'site': False,
}


def perioada_zi(ora):
    if 0 <= ora < 6:
        return 'noapte'
    if 6 <= ora < 12:
        return 'dimineata'
    if 12 <= ora < 18:
        return 'pranz'
    return 'seara'


def anotimp(luna):
    if luna in (12, 1, 2):
        return 'iarna'
    if luna in (3, 4, 5):
        return 'primavara'
    if luna in (6, 7, 8):
        return 'vara'
    return 'toamna'


conn = sqlite3.connect('./data/case/case_curate.sqlite3')

tabele = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table'",
    conn)['name'].tolist()

toate = []
for nume_tabel in tabele:
    df = pd.read_sql_query(f'SELECT * FROM "{nume_tabel}"', conn)

    if 'casa' not in df.columns:
        df['casa'] = nume_tabel

    if not df['casa'].astype(str).str.startswith('casa_').all():
        continue

    if 'categorie' not in df.columns:
        df['categorie'] = None

    df['timp_consum'] = pd.to_datetime(df['timp_consum']).dt.floor('h')

    df_orar = df.groupby(
        ['casa', 'id_appliance', 'Name', 'categorie', 'timp_consum'],
        as_index=False)['consum'].sum()
    toate.append(df_orar)

conn.close()

profil = pd.concat(toate, ignore_index=True)

profil['hour'] = profil['timp_consum'].dt.hour
profil['dayofweek'] = profil['timp_consum'].dt.dayofweek
profil['month'] = profil['timp_consum'].dt.month

profil['perioada_zi'] = profil['hour'].apply(perioada_zi)
profil['weekend'] = profil['dayofweek'] >= 5
profil['anotimp'] = profil['month'].apply(anotimp)
profil['controlabil'] = profil['categorie'].map(CONTROLABIL)

profil['timp_consum'] = profil['timp_consum'].astype(str)

conn_out = sqlite3.connect('./data/case/case_profil_orar.sqlite3')
profil.to_sql('profil_orar', conn_out, index=False, if_exists='replace')
conn_out.close()


