import sqlite3
import pandas as pd


CATEGORII = ('spalat', 'vase', 'uscator')
PRAGURI_PORNIT = {'spalat': 100, 'uscator': 60, 'vase': 60}
INTERVALE = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 300, 400, 1500]


def procent_zero(consum):
    return round(100 * (consum == 0).mean(), 2)


def procent_activ(activ):
    return round(100 * activ.mean(), 2)


def ore_pe_saptamana(activ):
    return round(activ.sum() * 10 / 60 / 53, 1)


conn = sqlite3.connect('./data/case/case_curate.sqlite3')

query = """
SELECT name
FROM sqlite_master
WHERE type='table'
"""
tabele = pd.read_sql_query(query, conn)['name'].tolist()

toate = []
for nume_tabel in tabele:
    query = f"""
    SELECT categorie, consum
    FROM "{nume_tabel}"
    WHERE categorie IN {CATEGORII}
    """
    df_casa = pd.read_sql_query(query, conn)
    df_casa.insert(0, 'casa', nume_tabel)
    toate.append(df_casa)

conn.close()

df_consum = pd.concat(toate, ignore_index=True)
df_consum['prag'] = df_consum['categorie'].map(PRAGURI_PORNIT)
df_consum['activ'] = df_consum['consum'] > df_consum['prag']

# cat de des sta aparatul pe zero, cat de des e activ si cate ore lucreaza pe saptamana
df_rezumat = df_consum.groupby(['casa', 'categorie']).agg(
    pct_zero=('consum', procent_zero),
    pct_activ=('activ', procent_activ),
    ore_pe_saptamana=('activ', ore_pe_saptamana),
)
print('=== Activari pe casa si categorie ===')
print(df_rezumat.to_string())

# distributia consumului nenul, ca sa vedem unde se rupe standby-ul de lucru
df_nenule = df_consum[df_consum['consum'] > 0].copy()
df_nenule['interval'] = pd.cut(df_nenule['consum'], bins=INTERVALE)

df_distributie = (df_nenule.groupby(['categorie', 'interval'], observed=True)
                  .size()
                  .unstack(fill_value=0))
df_distributie_pct = (100 * df_distributie.div(df_distributie.sum(axis=1), axis=0)).round(1)
#print(df_distributie_pct)

print('=== Valea dintre varful de standby si varful de lucru ===')
for categorie in df_distributie_pct.index:
    linie = df_distributie_pct.loc[categorie]
    print(linie)
    varf_standby = linie.index.get_loc(linie.iloc[:5].idxmax())
    print(varf_standby)
    varf_lucru = linie.index.get_loc(linie.iloc[5:].idxmax())
    print(varf_lucru)
    vale = linie.iloc[varf_standby:varf_lucru].idxmin()
    print(f'  {categorie:10s} vale la {vale}')

