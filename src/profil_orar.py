import sqlite3
import pandas as pd

conn = sqlite3.connect('./data/case/case_curate.sqlite3')
conn_out = sqlite3.connect('./data/case/case_profil_orar.sqlite3')

tabele = pd.read_sql_query(
    """SELECT name 
    FROM sqlite_master 
    WHERE type='table'""", 
    conn)['name'].tolist()

toate = []
for nume_tabel in tabele:
    df = pd.read_sql_query(f'SELECT * FROM "{nume_tabel}"', conn)

    if 'casa' not in df.columns:
        df['casa'] = nume_tabel

    if not df['casa'].astype(str).str.startswith('casa_').all():
        continue

    df['timp_consum'] = pd.to_datetime(df['timp_consum']).dt.floor('h')

    df_orar = df.groupby(['casa', 'id_appliance', 'Name', 'timp_consum'], as_index=False)['consum'].sum()
    toate.append(df_orar)

profil = pd.concat(toate, ignore_index=True)

profil = profil.groupby(['casa', 'id_appliance', 'Name', 'timp_consum'], as_index=False)['consum'].sum()

profil['hour'] = profil['timp_consum'].dt.hour
profil['dayofweek'] = profil['timp_consum'].dt.dayofweek
profil['month'] = profil['timp_consum'].dt.month

profil['timp_consum'] = profil['timp_consum'].astype(str)


for casa, grup in profil.groupby('casa'):
    grup = grup.drop(columns=['casa'])
    grup.to_sql(casa, conn_out, index=False, if_exists='replace')

conn.close()
conn_out.close()
