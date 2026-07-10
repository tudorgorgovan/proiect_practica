import os
import sqlite3
import pandas as pd 


# connect to database

conn = sqlite3.connect('./data/irise38.sqlite3')

house = 'House'
appliance = 'Appliance'
consumption = 'Consumption'

#JOIN intre Aplliance, House si Consumption pentru a obtine toate consumatoarele si consumul lor pe fiecare casa
query = """
SELECT 
    apl.ID as id_appliance,
    apl.HouseIDREF,
    apl.Name,
    h.StartingEpochTime,
    h.EndingEpochTime,
    ROUND((h.EndingEpochTime - h.StartingEpochTime) / (60 * 60 * 24.0), 3) AS durata_timp,
    c.value as consum,
    datetime(c.EpochTime, 'unixepoch') as timp_consum
FROM Appliance as apl
INNER JOIN House as h
    ON apl.HouseIDREF = h.ID
INNER JOIN Consumption as c
    ON apl.ID = c.ApplianceIDREF AND c.HouseIDREF = h.ID    
"""

df = pd.read_sql_query(query, conn)
conn.close()

# Pentru fiecare casa distincta, salveaza consumatoarele ei intr-o baza de date SQLite separata 
cheie_unica_casa = df['HouseIDREF'].unique()

folder_casa = f"./data/case"
for id_casa in cheie_unica_casa:
    df_casa = df[df['HouseIDREF'] == id_casa]
    folder_casa = f"data/case/casa_{id_casa}"
    os.makedirs(folder_casa, exist_ok=True)

    cale_db = f"{folder_casa}/casa_{id_casa}.db"
    conn_casa = sqlite3.connect(cale_db)    
    df_casa.to_sql('aplienceuri_casa', conn_casa, index=False, if_exists='replace')

    conn_casa.close()