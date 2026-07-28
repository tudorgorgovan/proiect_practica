import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px

conn = sqlite3.connect('./data/case/case_profil_orar.sqlite3')
cursor = conn.cursor()
query = """
SELECT name
FROM sqlite_master
WHERE type='table';
"""

cursor.execute(query)
tabel = cursor.fetchall()
df_tabele = pd.read_sql_query(f'SELECT DISTINCT casa FROM "{tabel[0][0]}"', conn)

query = """
SELECT 
    casa,
    ROUND(SUM(consum)/1000/24, 2) AS total_consum_kWh_per_zi
FROM profil_orar
WHERE Name NOT LIKE '%Site consumption%' AND Name NOT LIKE 'Total site%'
GROUP BY casa
"""

df_total = pd.read_sql_query(query, conn)
#print(df_total)

query = """
SELECT casa,
    ROUND(SUM(consum)/1000/24, 2) AS ctrb_kWh_per_zi
FROM profil_orar
WHERE controlabil = 1 
GROUP BY casa
"""
df_apl_ctrb = pd.read_sql_query(query, conn)
#print(df_apl_ctrb)

print((df_apl_ctrb['ctrb_kWh_per_zi']/df_total['total_consum_kWh_per_zi']).round(3).sort_values(ascending=False)*100)    
   
df_total['pondere'] = df_apl_ctrb['ctrb_kWh_per_zi'] / df_total['total_consum_kWh_per_zi'] * 100
df_total = df_total.sort_values('pondere', ascending=False)

px.bar(df_total, x='casa', y='pondere', text=df_total['pondere'].round(2), title='Ponderea consumului controlabil din consumul total', labels={'casa': 'Casa', 'pondere': 'Pondere (%)'}, color='pondere').show()