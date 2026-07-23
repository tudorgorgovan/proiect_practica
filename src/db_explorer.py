import os
import sqlite3
import pandas as pd 

# connect to database

conn = sqlite3.connect('./data/irise38.sqlite3')

#JOIN intre Aplliance, House si Consumption pentru a obtine toate consumatoarele si consumul lor pe fiecare casa
query = """
SELECT 
    apl.ID as id_appliance,
    apl.HouseIDREF,
    apl.Name, 
    c.value as consum,
    c.EpochTime as epoch
FROM Appliance as apl
INNER JOIN House as h
    ON apl.HouseIDREF = h.ID
INNER JOIN Consumption as c
    ON apl.ID = c.ApplianceIDREF AND c.HouseIDREF = h.ID    
"""

df = pd.read_sql_query(query, conn)
df['timp_consum'] = pd.to_datetime(df['epoch'], unit='s', utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
df['hour'] = df['timp_consum'].dt.hour
df['dayofweek'] = df['timp_consum'].dt.dayofweek
df['month'] = df['timp_consum'].dt.month
df.drop(columns=['epoch'], inplace=True)

# Pentru fiecare casa distincta, salveaza consumatoarele ei intr-o baza de date SQLite separata 
cheie_unica_casa = df['HouseIDREF'].unique()

os.makedirs("./data/case", exist_ok=True)
for id_casa in cheie_unica_casa:
    df_casa = df[df['HouseIDREF'] == id_casa]
    del(df_casa['HouseIDREF'])
    conn_casa = sqlite3.connect(f"./data/case/case.sqlite3")    
    df_casa.to_sql(f'casa_{id_casa}', conn_casa, index=False, if_exists='replace')

    conn_casa.close()
    
query = """
SELECT
    ID,
    StartingEpochTime,
    EndingEpochTime,
    ROUND((EndingEpochTime - StartingEpochTime) / (60 * 60 * 24.0), 3) AS durata_timp
    
FROM House;
"""
df_durata = pd.read_sql_query(query, conn)
df_durata['inceput_timp'] = pd.to_datetime(df_durata['StartingEpochTime'], unit='s', utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
df_durata['final_timp'] = pd.to_datetime(df_durata['EndingEpochTime'], unit='s', utc=True).dt.tz_convert('Europe/Paris').dt.tz_localize(None)
df_durata = df_durata.drop(columns=['StartingEpochTime', 'EndingEpochTime'])

df_toate_casele = df_durata[df_durata['ID'].isin(cheie_unica_casa)]

os.makedirs("./outputs", exist_ok=True)
df_toate_casele.to_csv("./outputs/durata_case.csv", index=False)
conn.close()