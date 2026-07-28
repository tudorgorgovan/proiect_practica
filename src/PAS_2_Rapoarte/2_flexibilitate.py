import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px

conn = sqlite3.connect('./data/case/case_profil_orar.sqlite3')
cursor = conn.cursor()
query = """
SELECT casa,
    COUNT(DISTINCT id_appliance) AS nr_aparate
FROM profil_orar
WHERE controlabil = 1
GROUP BY casa

"""
df_apl_ctrb = pd.read_sql_query(query, conn)
#print(df_apl_ctrb)

px.bar(df_apl_ctrb.sort_values('nr_aparate', ascending=False), x='casa', y='nr_aparate',color = 'nr_aparate').show()