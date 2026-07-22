import os
import sqlite3
import pandas as pd

REGULI_CATEGORII = [
    ("site consumption", "site"),
    ("light consumption", "total_light"),
    ("microwave", "microunde"),
    ("fridge", "frigider"),
    ("freezer", "frigider"),
    ("washing", "spalat"),
    ("dish", "vase"),
    ("drier", "uscator"),
    ("water heater", "boiler_el"),
    ("electric heating", "incalzire"),
    ("cooker", "plita"),
    ("hot plate", "plita"),
    ("oven", "cuptor"),
    ("boiler", "pompa_boiler"),
    ("lamp", "lampa"),
    ("tv", "tv"),
]

PRAGURI = {
    "frigider": 800,
    "spalat": 2800,
    "vase": 3000,
    "uscator": 3500,
    "boiler_el": 3500,
    "incalzire": 9000,
    "plita": 7000,
    "cuptor": 3500,
    "microunde": 2000,
    "tv": 400,
    "lampa": 800,
    "pompa_boiler": 600,
    "total_light": 3000,
    "site": 15000,
    "alt": float("inf"),
}


def clasifica(nume_aparat):
    nume = nume_aparat.lower()
    for cuvant, categorie in REGULI_CATEGORII:
        if cuvant in nume:
            return categorie
    return "alt"


conn = sqlite3.connect('./data/case/case.sqlite3')
cursor = conn.cursor()

query_tabele = """
SELECT name
FROM sqlite_master
WHERE type='table'
"""
cursor.execute(query_tabele)
tabele = cursor.fetchall()

conn_curat = sqlite3.connect('./data/case/case_curat.sqlite3')

raport = []
neclasificate = set()

for table_name in tabele:
    nume_tabel_sursa = table_name[0]
    query_select = f'SELECT * FROM "{nume_tabel_sursa}";'
    df = pd.read_sql_query(query_select, conn)

    df['categorie'] = df['Name'].apply(clasifica)
    df['prag'] = df['categorie'].map(PRAGURI)

    masca_outlier = df['consum'] > df['prag']
    df.loc[masca_outlier, 'consum'] = pd.NA

    for (nume_apl, categ), grup in df.groupby(['Name', 'categorie']):
        taiate = grup['consum'].isna().sum()
        if taiate > 0:
            raport.append({
                'casa': nume_tabel_sursa,
                'aparat': nume_apl,
                'categorie': categ,
                'puncte_taiate': int(taiate),
            })
        if categ == 'alt':
            neclasificate.add(nume_apl)

    df = df.drop(columns=['prag'])
    df.to_sql(nume_tabel_sursa, conn_curat, index=False, if_exists='replace')

conn.close()
conn_curat.close()

df_raport = pd.DataFrame(raport).sort_values('puncte_taiate', ascending=False)

os.makedirs('./outputs', exist_ok=True)
df_raport.to_csv('./outputs/raport_outlieri.csv', index=False)
