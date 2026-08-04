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

- Am reparat fusul orar in [src/db_explorer.py](src/db_explorer.py): timpul era salvat in UTC (`datetime(epoch, 'unixepoch')`), ceea ce decala ora locala cu +1h iarna si +2h vara. Acum epoch-ul e citit ca UTC si convertit la `Europe/Paris` cu pandas (`tz_localize('UTC').tz_convert('Europe/Paris').tz_localize(None)`), care gestioneaza automat trecerea la ora de vara.
- Am verificat problema pe date inainte sa o repar: minimul de consum de noapte era decalat cu o ora intre iarna si vara, ceea ce e semnatura schimbarii orei. Dupa corectie decalajul a ajuns la zero.
- Am adaugat in `db_explorer.py` coloanele derivate `hour`, `dayofweek`, `month`, ca sa fie gata pentru profilul orar si analiza pe tip de zi / anotimp.
- Am creat fisierul nou [src/curatare_date.py](src/curatare_date.py): clasifica fiecare aparat pe categorie si taie valorile de consum peste pragul fizic al categoriei (le marcheaza `NaN`, nu cu media; zero-urile raman). Salveaza datele curate in `case_curat.sqlite3`, fara sa atinga datele brute, si un raport in `outputs/raport_outlieri.csv`.

# Progres - 23 iulie 2026

## Ce am facut

- Am completat valorile lipsa in [src/curatare_date.py](src/curatare_date.py): outlierii nu mai raman `NaN`, ci dupa ce sunt taiati (peste prag) sunt inlocuiti cu media aparatului din aceeasi casa (media pe valorile ramase, grupat pe `casa` + `id_appliance`). Astfel `case_curate.sqlite3` contine direct valori modificate, fara `NaN`.
- Am extins raportul de outlieri (`outputs/raport_outlieri.csv`): pe langa `casa`, `aparat`, `categorie`, `puncte_taiate`, am adaugat `valoare_medie` (media pusa in loc) si `date_taiate` (lista datelor/`timp_consum` la care s-a facut inlocuirea). Total taiat: 37 puncte.
- Am ajustat pragurile per categorie in `curatare_date.py` (ex. `plita` 800, `spalat`/`vase` 1500, `uscator`/`cuptor`/`microunde` 1000, `boiler_el` 2500) ca sa elimine varfurile nefizice.
- Am creat/reparat [src/profil_orar.py](src/profil_orar.py): agrega datele curate de la rezolutie 10 min la 1 ora (suma celor 6 citiri), pe fiecare aparat, si salveaza `case_profil_orar.sqlite3` cu un tabel per casa. Facut robust la structura intrarii (detecteaza coloana `casa`; daca lipseste, numele tabelului e casa; sare peste tabele care nu incep cu `casa_`).

## TERMINAT PASUL 1 - Curatarea si agregarea datelor.

# Progres - 26 iulie 2026

- Bazat pe fisierul `1_pondere_consum.py` putem afla cat de mult din consum este realizat de aplianceuri controlabile. Astfel, `casa907` are 99.3%, `casa904` are 83,86% si `casa902` are 76%.
- Bazat pe fisierul `2_flexibilitate.py` putem afla cate aplianceuri controlabile fiecare casa si care, clasandu-le in ordine descrescatoare dupa numarul acestora. O intrebare importanta la care raspunde acest script este: "Care casa are boiler?". Astfel, casele care au boiler sunt: casa907 cu 4 aplianceuri controlabile; casa904 cu 3 aplianceuri controlabile; casa909 cu 3 aplianceuri controlabile; casa902 cu 3 aplianceuri; casa900 cu 2 aplianceuri controlabile.

**Ranking pana acum**: 
  1) casa907
  2) casa904
  3) casa902

# Progres - 28 iulie 2026

- Am creat fisierul [src/PAS_2_Rapoarte/3_praguri_activari.py](src/PAS_2_Rapoarte/3_praguri_activari.py) ca sa stabilesc de la ce consum spun ca un aparat chiar functioneaza. Pana acum foloseam "consum diferit de zero", dar asta include si standby-ul (temporizator, electronica, pompa in repaus), nu doar functionarea reala.
- M-am uitat la distributia valorilor nenule si e bimodala: un varf jos, pe la 10-20 W, care e standby-ul, si unul sus, pe la 200-400 W, care e functionarea. Am pus pragul in valea dintre cele doua varfuri, acolo unde sunt cele mai putine masuratori, ca sa fie decizia cat mai stabila.
- Valea nu e in acelasi loc la toate aparatele, asa ca am facut pragurile pe categorie: `spalat` 100 W, `uscator` 60 W, `vase` 60 W. Masina de spalat are o coada mai lunga de valori mici (probabil motorul la turatie mica), de aia pragul ei e mai sus.
- Am validat pragul cu un test simplu: cu prag de 10 W, casa902 ar iesi ca spala 19 ore pe saptamana, adica aproape 3 ore in fiecare zi, ceea ce e imposibil. Cu pragul din vale iese 4 ore pe saptamana, adica vreo 3 cicluri, ceea ce are sens.
- In acelasi fisier am calculat `pct_zero`, `pct_activ` si `ore_pe_saptamana` per casa si categorie. Aparatele astea stau oprite 93-97% din timp, deci au cicluri clare si merita analizate ca evenimente.
- Ce am observat: uscatorul e folosit de 2-3 ori mai multe ore decat masina de spalat (la casa907, 12.6 ore pe saptamana fata de 3). Deci uscatorul e de fapt aparatul cu cel mai mare potential de mutare, nu masina de spalat cum credeam.
- Am scos din calcul casa910 (0.2 ore pe saptamana) si casa900 (1 ora), pentru ca aparatele lor practic nu sunt folosite si nu am ce modela acolo.

# Progres - 29 iulie 2026

- Am creat fisierul [src/PAS_2_Rapoarte/4_ore_utilizare.py](src/PAS_2_Rapoarte/4_ore_utilizare.py): calculeaza probabilitatea ca un aparat sa functioneze la fiecare ora a zilei, separat pe zile lucratoare si weekend.
- Unitatea de observatie e ziua, nu masuratoarea. Daca as numara masuratori, un ciclu de o ora ar conta de 6 ori (sunt citiri la 10 minute) si as masura durata in loc de frecventa. Asa, pentru fiecare zi aparatul ori a mers la ora aia, ori nu.
- Cand pun toate casele la un loc am nevoie de coloana `casa_zi`, pentru ca data `1998-05-03` apare la toate cele 14 case si `nunique()` pe `zi` le-ar contopi. Cand `casa` e deja in grupare pot folosi direct `zi`.
- Am adaugat si o grila completa pe cele 24 de ore, pentru ca dupa `groupby` combinatiile fara nicio utilizare lipsesc cu totul si barele dispareau din grafic in loc sa fie zero.
- Rezultatul: masina de spalat are varful dimineata (9-11), uscatorul la pranz (13) si masina de vase seara (20-21). Deci apar in ordinea normala dintr-o gospodarie, intai speli, apoi usuci, apoi speli vasele dupa cina. Mi se pare cea mai buna verificare ca pragurile prind comportament real.
- La weekend varful masinii de spalat se muta cu vreo 2 ore mai tarziu (de la 8 la 10) si e mai inalt, iar in zilele lucratoare apare un al doilea varf pe la 17-18, dupa program.

# Progres - 30 iulie 2026

- Am creat fisierul [src/PAS_2_Rapoarte/5_probabilitati.py](src/PAS_2_Rapoarte/5_probabilitati.py), care acopera ce mai ramasese din notite: probabilitatea de functionare in functie de perioada zilei, tipul zilei si anotimp.
- Am folosit perioada zilei (noapte, dimineata, pranz, seara) in loc de ora. Cu 24 de ore x 2 tipuri de zi x 4 anotimpuri ar fi iesit 192 de combinatii si cam 2 zile in fiecare, ceea ce nu se poate folosi. Cu 4 perioade raman 32 de combinatii si intre 26 si 66 de zile in fiecare.
- Partea la care a trebuit sa fiu atent e numitorul. Anotimpul si tipul zilei impart zilele (o zi e ori vara, ori iarna), deci intra in numitor. Perioada zilei e in interiorul zilei (fiecare zi are toate cele 4 perioade), deci nu intra. Numitorul e numarul de ocazii, nu numarul de combinatii.
- Am verificat pe date: vara imi da 66 de zile lucratoare si 26 de weekend per casa, ceea ce e corect pentru ~92 de zile de vara.
- Combinatiile fara nicio utilizare nu apar dupa `groupby`, asa ca am construit grila completa cu `MultiIndex.from_product` si `merge(how='cross')`, pornind de la perechile reale casa-categorie ca sa nu inventez aparate care nu exista in casa respectiva.
- Exemplul din notite (vara, dimineata, zi lucratoare, masina de spalat): casa902 iese 0.561 (37 de zile din 66), casa901 0.485, casa904 0.394, iar casa903 doar 0.091.
- Tiparul pe perioade confirma ce vazusem pe ore: spalatul are varful dimineata, uscatorul la pranz, vasele seara. La spalat, dimineata, iese 0.47 in weekend fata de 0.35 in zilele lucratoare, deci tipul zilei chiar conteaza si nu poate fi scos din model.
- Observatia care mi se pare cea mai importanta: potentialul nu inseamna comportament. casa909 are 73% consum controlabil si arata bine la prima vedere, dar aproape tot vine de la boiler si incalzire electrica, care pornesc de la termostat, nu de la om. Daca ma uit doar la aparatele pornite de locatar, casa909 cade de pe locul 4 pe locul 7.

## TERMINAT PASUL 2 - KPI-uri de selectie si probabilitati de utilizare.

# Progres - 4 august 2026

- Am ales casa901 pentru model: are toate cele trei categorii pornite de om si nu are boiler sau incalzire electrica.

- Aparatele stau pe exact zero cand sunt oprite (95.3% din masuratorile masinii de spalat). Valorile 10-100 pe care le luasem drept standby sunt clatirea si centrifuga, iar banda aia e mai lunga decat cea de peste 100.

- Am trecut la doua praguri: `PRAG_JOS = 5` pentru capetele ciclului, `PRAGURI_PORNIT` pe categorie pentru confirmare. Cu prag unic, un ciclu de 110 minute din casa901 iesea de 50 de minute si pierdea 14% din energie.

- Am creat [src/PAS_3_Model/6_cicluri.py](src/PAS_3_Model/6_cicluri.py): citeste `case_curate.sqlite3`, grupeaza masuratorile consecutive de peste `PRAG_JOS` si scoate un rand per ciclu (`start`, `sfarsit`, `energie_wh`, `varf`, `durata_min`) plus `ora_start`, `tip_zi`, `anotimp`, `perioada_zi`, `saptamana`. Salveaza in `cicluri.sqlite3`. Gruparea e per aparat si se rupe la pauzele din inregistrare.

- Unitatea de observatie devine evenimentul: cele 54404 de masuratori ale masinii de spalat din casa901 dau 254 de cicluri.

