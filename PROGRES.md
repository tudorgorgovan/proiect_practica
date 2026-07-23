# Progres - 10 iulie 2026

## Ce am facut

- Am creat fisierul [src/db_explorer.py](src/db_explorer.py) pentru a extrage datele per casa din baza de date sursa si a le salva separat:
  - Facut JOIN intre tabelele `Appliance` si `House` (dupa `HouseIDREF`), extragand pentru fiecare aparat: id, casa, nume, timpii de start/sfarsit si durata.
  - Pentru fiecare casa distincta (`HouseIDREF`), s-a creat un folder propriu in `data/case/casa_<id>/` si o baza de date SQLite separata (`casa_<id>.db`) continand tabela `aplienceuri_casa` cu aparatele acelei case.
  - Rezultat: 14 baze de date generate, una per casa (`casa_2000900` ... `casa_2000913`).
- Am extins query-ul SQL din [src/db_explorer.py](src/db_explorer.py) cu un `INNER JOIN` suplimentar pe tabela `Consumption` (dupa `ApplianceIDREF` si `HouseIDREF`), adaugand coloanele `consum` (`value`) si `timp_consum` (`EpochTime`), astfel incat bazele de date per casa sa contina si datele de consum pentru fiecare aparat.
- Am ajustat formatul coloanelor din query: `durata_timp` este acum exprimata in zile (`ROUND(... / (60*60*24.0), 3)`) in loc de secunde brute, iar `timp_consum` este convertit din epoch in format `datetime` lizibil (`datetime(c.EpochTime, 'unixepoch')`).

# Progres - 11 iulie 2026

## Ce am facut

- Am rescris query-ul principal din [src/db_explorer.py](src/db_explorer.py): am scos `Name` si coloanele de durata (`StartingEpochTime`, `EndingEpochTime`, `durata_timp`) din selectul pe aparate si am adaugat un query separat, pe tabela `House`, care calculeaza durata fiecarei case intr-un `df_durata` distinct.
- Am schimbat modul de stocare: in loc sa creez cate un fisier `.db` separat pentru fiecare casa (14 fisiere), acum toate casele sunt salvate intr-un singur fisier `data/case/case.sqlite3`, fiecare casa avand propriul tabel (`casa_<id>`).
- Durata caselor nu mai e salvata in baze de date separate per casa, ci exportata o singura data intr-un fisier `data/case/durata_case.csv`, filtrat doar pe casele care apar efectiv in date.
- Am creat fisierul nou [src/db_extraction.py](src/db_extraction.py): citeste `case.sqlite3`, parcurge fiecare tabel/casa, extrage aparatele unice (`id_appliance`) si salveaza fiecare aparat intr-un tabel separat (numit dupa `Name`) intr-o baza de date per casa.

# Progres - 12 iulie 2026

## Ce am facut

- Am mutat bazele de date generate pentru aparate in [src/db_extraction.py](src/db_extraction.py) intr-un folder dedicat, `data/case/aplianceuri/`, in loc sa fie amestecate cu `case.sqlite3`.
- Am redus datele salvate per aparat doar la coloanele relevante (`consum`, `timp_consum`), in loc sa salvez tot `df`-ul aparatului (care mai continea si coloane redundante precum `id_appliance` sau `HouseIDREF`).

# Progres - 13 iulie 2026

## Ce am facut

- Am actualizat `.gitignore` sa ignore si folderul `grafice/` (unde se salveaza graficele generate).
- Am scos coloana `HouseIDREF` din tabelele per casa salvate in `case.sqlite3` prin [src/db_explorer.py](src/db_explorer.py), fiind redundanta (fiecare tabel e deja specific unei singure case).
- Am creat fisierul nou [src/db_to_grafice.py](src/db_to_grafice.py): citeste toate tabelele (casele) din `case.sqlite3` si genereaza, pentru fiecare, un grafic interactiv Plotly (consum in timp, cate o linie per aparat) cu un dropdown care permite selectarea aparatului afisat; fiecare grafic e salvat ca fisier HTML in folderul `grafice/`.

# Progres - 22 iulie 2026

## Ce am facut

- **Reparat fusul orar** in [src/db_explorer.py](src/db_explorer.py): timpul era salvat in UTC (`datetime(epoch, 'unixepoch')`), ceea ce decala ora locala cu +1h iarna / +2h vara. Acum epoch-ul e citit ca UTC si convertit la `Europe/Paris` cu pandas (`tz_localize('UTC').tz_convert('Europe/Paris').tz_localize(None)`), care gestioneaza automat trecerea la ora de vara.

- Am adaugat in `db_explorer.py` coloanele derivate `hour`, `dayofweek`, `month`, ca sa fie gata pentru profilul orar si analiza pe tip de zi / anotimp.

- **Am creat fisierul nou [src/curatare_date.py](src/curatare_date.py)**: clasifica fiecare aparat pe categorie si taie valorile de consum peste pragul fizic al categoriei (le marcheaza `NaN`, nu cu media; zero-urile raman). Salveaza datele curate in `case_curat.sqlite3`, fara sa atinga datele brute, si un raport in `outputs/raport_outlieri.csv`.

# Progres - 23 iulie 2026

## Ce am facut

- **Completarea valorilor lipsa in fisierul [src/curatare_date.py](src/curatare_date.py)**: outlierii nu mai raman `NaN` — dupa ce sunt taiati (peste prag) sunt inlocuiti cu media aparatului din aceeasi casa (media pe valorile ramase, grupat pe `casa` + `id_appliance`). Astfel `case_curate.sqlite3` contine direct valori modificate, fara `NaN`. 

- **Raport de outlieri extins** (`outputs/raport_outlieri.csv`): pe langa `casa`, `aparat`, `categorie`, `puncte_taiate`, am adaugat `valoare_medie` (media pusa in loc) si `date_taiate` (lista datelor/`timp_consum` la care s-a facut inlocuirea). Total taiat: 37 puncte.

- **Ajustat pragurile per categorie** in `curatare_date.py` (ex. `plita` 800, `spalat`/`vase` 1500, `uscator`/`cuptor`/`microunde` 1000, `boiler_el` 2500) ca sa elimine varfurile nefizice.

- **Am creat/reparat [src/profil_orar.py](src/profil_orar.py)**: agregă datele curate de la rezolutie 10 min la 1 ora (suma celor 6 citiri), pe fiecare aparat, si salveaza `case_profil_orar.sqlite3` cu un tabel per casa. Facut robust la structura intrarii (detecteaza coloana `casa`; daca lipseste, numele tabelului e casa; sare peste tabele care nu incep cu `casa_`).


