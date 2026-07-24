import sqlite3
import pandas as pd
import os


conn = sqlite3.connect('./data/case/case_curate.sqlite3')
cursor = conn.cursor()

query_tabele = """
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
"""
cursor.execute(query_tabele)
tabele = cursor.fetchall()

rezultate = []
for table_name in tabele:
    nume_tabel_sursa = table_name[0]

    query_select = f'SELECT consum FROM "{nume_tabel_sursa}" WHERE Name = "Site consumption ()";'
    df = pd.read_sql_query(query_select, conn)

    descriere = df['consum'].describe()
    descriere['casa'] = nume_tabel_sursa
    rezultate.append(descriere)


tabel = pd.DataFrame(rezultate)
tabel = tabel[['casa', 'count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
tabel = tabel.sort_values('max').reset_index(drop=True)

print('Consum total per casa - "Site consumption ()"')
print(tabel.to_string(index=False))

os.makedirs('./outputs', exist_ok=True)
tabel.to_csv('./outputs/analiza_calitate.csv', index=False)

conn.close()
