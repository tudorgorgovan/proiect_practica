import os
import sqlite3
import pandas as pd


conn = sqlite3.connect('./data/case/case.sqlite3')

cursor = conn.cursor()

query = """
SELECT name 
FROM sqlite_master 
WHERE type='table';
"""
for table_name in cursor.execute(query):
    nume_tabel = table_name[0]
    query = f"""
    SELECT * 
    FROM {nume_tabel};
    """
    
    df = pd.read_sql_query(query, conn)
    nr_appliance = df['id_appliance'].unique()
    for id in nr_appliance:
        df_appliance = df[df['id_appliance'] == id]
        connection = sqlite3.connect(f'./data/case/casa_{df_appliance["HouseIDREF"].iloc[0]}.sqlite3')
        df_appliance.to_sql(f'{df_appliance["Name"].iloc[0]}', connection, index=False, if_exists='replace')