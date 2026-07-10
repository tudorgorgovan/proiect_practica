# Progres - 10 iulie 2026

## Ce am facut

- Am creat fisierul [src/db_explorer.py](src/db_explorer.py) pentru a extrage datele per casa din baza de date sursa si a le salva separat:
  - Facut JOIN intre tabelele `Appliance` si `House` (dupa `HouseIDREF`), extragand pentru fiecare aparat: id, casa, nume, timpii de start/sfarsit si durata.
  - Pentru fiecare casa distincta (`HouseIDREF`), s-a creat un folder propriu in `data/case/casa_<id>/` si o baza de date SQLite separata (`casa_<id>.db`) continand tabela `aplienceuri_casa` cu aparatele acelei case.
  - Rezultat: 14 baze de date generate, una per casa (`casa_2000900` ... `casa_2000913`).
- Am extins query-ul SQL din [src/db_explorer.py](src/db_explorer.py) cu un `INNER JOIN` suplimentar pe tabela `Consumption` (dupa `ApplianceIDREF` si `HouseIDREF`), adaugand coloanele `consum` (`value`) si `timp_consum` (`EpochTime`), astfel incat bazele de date per casa sa contina si datele de consum pentru fiecare aparat.
- Am ajustat formatul coloanelor din query: `durata_timp` este acum exprimata in zile (`ROUND(... / (60*60*24.0), 3)`) in loc de secunde brute, iar `timp_consum` este convertit din epoch in format `datetime` lizibil (`datetime(c.EpochTime, 'unixepoch')`).

