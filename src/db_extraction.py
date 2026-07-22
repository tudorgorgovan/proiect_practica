import sqlite3
import pandas as pd
import os


conn = sqlite3.connect('./data/case/case.sqlite3')
cursor = conn.cursor()

query_tabele = """
SELECT name 
FROM sqlite_master 
WHERE type='table';
"""
cursor.execute(query_tabele)
tabele = cursor.fetchall()
os.makedirs(f'./data/case/aplianceuri', exist_ok=True)
for table_name in tabele:
    nume_tabel_sursa = table_name[0]
    query_select = f'SELECT * FROM "{nume_tabel_sursa}";'
    df = pd.read_sql_query(query_select, conn)
    
    nr_appliance = df['id_appliance'].unique()
    for id in nr_appliance:
        df_appliance = df[df['id_appliance'] == id]
        nume_appliance = df_appliance["Name"].iloc[0]
        df_de_salvat = df_appliance[['consum', 'timp_consum']]

        connection = sqlite3.connect(f'./data/case/aplianceuri/{nume_tabel_sursa}.sqlite3')
        df_de_salvat.to_sql(nume_appliance, connection, index=False, if_exists='replace')
        connection.close()

conn.close()