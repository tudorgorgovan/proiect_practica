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
    "spalat": 1500,
    "vase": 1500,
    "uscator": 1000,
    "boiler_el": 2500,
    "incalzire": 900,
    "plita": 800,
    "cuptor": 1000,
    "microunde": 1000,
    "tv": 400,
    "lampa": 800,
    "pompa_boiler": 600,
    "total_light": 3000,
    "site": 15000,
}

def clasifica(nume_aparat):
    nume = nume_aparat.lower()
    for cuvant, categorie in REGULI_CATEGORII:
        if cuvant in nume:
            return categorie

conn = sqlite3.connect('./data/case/case.sqlite3')
tabele = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)['name'].tolist()

toate = []
for nume_tabel_sursa in tabele:
    df = pd.read_sql_query(f'SELECT * FROM "{nume_tabel_sursa}"', conn)
    df.insert(0, 'casa', nume_tabel_sursa)
    df['categorie'] = df['Name'].apply(clasifica)
    toate.append(df)
conn.close()

date = pd.concat(toate, ignore_index=True)
date['prag'] = date['categorie'].map(PRAGURI)

raport = []

masca_outlier = date['consum'] > date['prag']
taiate_info = date.loc[masca_outlier, ['casa', 'id_appliance', 'Name', 'categorie', 'timp_consum', 'consum']].copy()

date.loc[masca_outlier, 'consum'] = pd.NA
medie = date.groupby(['casa', 'id_appliance'])['consum'].transform('mean')
date['consum'] = date['consum'].fillna(medie)

for (casa, nume_apl, categorie), g in taiate_info.groupby(['casa', 'Name', 'categorie']):
    id_apl = g['id_appliance'].iloc[0]
    val_medie = date.loc[(date['casa'] == casa) & (date['id_appliance'] == id_apl), 'consum'].mean()
    raport.append({
        'casa': casa,
        'aparat': nume_apl,
        'categorie': categorie,
        'puncte_taiate': len(g),
        'valoare_medie': round(float(val_medie)),
        'date_taiate': '; '.join(g['timp_consum'].astype(str).tolist()),
    })

date = date.drop(columns=['prag'])
conn_curat = sqlite3.connect('./data/case/case_curate.sqlite3')

for casa, grup in date.groupby('casa'):
    grup = grup.drop(columns=['casa'])
    grup.to_sql(casa, conn_curat, index=False, if_exists='replace')
conn_curat.close()

df_raport = pd.DataFrame(raport).sort_values('puncte_taiate', ascending=False)

os.makedirs('./outputs', exist_ok=True)
df_raport.to_csv('./outputs/raport_outlieri.csv', index=False)
