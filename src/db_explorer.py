import os
import sqlite3
import pandas as pd 
import csv

# connect to database

conn = sqlite3.connect('./data/irise38.sqlite3')

#JOIN intre Aplliance, House si Consumption pentru a obtine toate consumatoarele si consumul lor pe fiecare casa
query = """
SELECT 
    apl.ID as id_appliance,
    apl.HouseIDREF,
    apl.Name, 
    c.value as consum,
    datetime(c.EpochTime, 'unixepoch') as timp_consum
FROM Appliance as apl
INNER JOIN House as h
    ON apl.HouseIDREF = h.ID
INNER JOIN Consumption as c
    ON apl.ID = c.ApplianceIDREF AND c.HouseIDREF = h.ID    
"""

df = pd.read_sql_query(query, conn)


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
    datetime(StartingEpochTime, 'unixepoch') as StartingEpochTime,
    datetime(EndingEpochTime, 'unixepoch') as EndingEpochTime,
    ROUND((EndingEpochTime - StartingEpochTime) / (60 * 60 * 24.0), 3) AS durata_timp
    
FROM House;
"""
df_durata = pd.read_sql_query(query, conn)

df_durata.to_csv("./data/case/durata_case.csv", index=False)
df_toate_casele = df_durata[df_durata['ID'].isin(cheie_unica_casa)]

df_toate_casele.to_csv("./data/case/durata_case.csv", index=False)
conn.close()