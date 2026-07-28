import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px

conn = sqlite3.connect('./data/case/case_profil_orar.sqlite3')
cursor = conn.cursor()
query = """
SELECT casa,
    categorie,
    COUNT(DISTINCT id_appliance) AS nr_aparate
FROM profil_orar
WHERE controlabil = 1
GROUP BY casa, categorie

"""
df_apl_ctrb = pd.read_sql_query(query, conn)
#print(df_apl_ctrb)
ordine = (df_apl_ctrb.groupby('casa')['nr_aparate']
          .sum()
          .sort_values(ascending=False)
          .index.tolist())
px.bar(df_apl_ctrb, x='casa', y='nr_aparate',color = 'categorie',category_orders={'casa': ordine}).show()