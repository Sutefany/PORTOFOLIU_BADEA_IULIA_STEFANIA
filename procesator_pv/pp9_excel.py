
############################### COMPLETAREA DOCUMENTULUI EXCEL CU DATE DIN DB ###############################

# un excel per saptamana pentru toate echipele -> denumire excel: SITUATIA GENERALA DE LUCRARI 12-10-2026 - 16-10-2026

### IMPORTURI NECESARE

import os

from openpyxl import load_workbook
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configurare_db import username, password
import shutil # PENTRU COPIEREA EXCELULUI MODEL
from pathlib import Path
from pp1_model import toate_pv

### CONECTAREA CU BAZA DE DATE

engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost:3306/proiect_personal")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# ###################################################################################
# PARTEA 9 - NORMALIZAREA DATEI DIN BAZA DE DATE
# ###################################################################################

# TODO 9a: STERGEREA TUTUROR TABELELOR - la fiecare rulare trebuie sterse si refacute pt. evitarea duplicatelor

RADACINA_PROIECT = Path(__file__).resolve().parent
FOLDER_EXPORTS = RADACINA_PROIECT / "exports"
FISIER_MODEL = RADACINA_PROIECT / "model_excel" / "MODEL.xlsx"

def sterge_tabele_excel():
    FOLDER_EXPORTS.mkdir(parents=True, exist_ok=True)
    fisiere_sterse = 0
    for fisier_excel in FOLDER_EXPORTS.glob("SITUATIA GENERALA DE LUCRARI *.xlsx"):
        try:
            fisier_excel.unlink()
            fisiere_sterse += 1
            print(f"Fișier șters: {fisier_excel.name}")
        except PermissionError:
            print(f"Nu pot șterge {fisier_excel.name}.Închide fișierul în Excel și încearcă din nou.")
            raise
    print(f"Au fost șterse {fisiere_sterse} fișiere Excel.")

# TODO 9b: stabilirea zilei de luni si de sambata pentru marcarea distinctiva a titlului
#  -> de la 2026-10-12, trebuie 12-10-2026
#  ->  trebuie sa stie cand incepe/se termina saptamana -> titlu potrivit: SITUATIA GENERALA DE LUCRARI 12-10-2026 - 16-10-2026
#                                                       -> completare in excel cu toate datele in celulele 2D-2I
#  -> ex: data intrare: 2026-10-13 -> return (datetime.date(2020, 10, 12), datetime.date(2020, 10, 17)), deci luni si sambata
#  -> nu se va converti data in string momentan deoarece trebuie mai tarziu formatul date -> se va converti doar la nevoie

def inceput_final_saptamana(data):

    luni = data - timedelta(days=data.weekday())   # calculeaza care este data zilei de luni
    sambata = luni + timedelta(days=5)             # calculeaza care este data zilei de sambata (luni + 5)
    return luni, sambata  # returneaza doua date de tip date => va sti ca "2026-10-14" pica in saptamana 12-16 OCTOMBRIE

# #######################################################################################
# PARTEA 9B - REALIZAREA TABELELOR EXCEL, PRELUAREA INFORMATIEI SI COMPLETAREA TABELELOR
# #######################################################################################

# TODO 9c: deschiderea sesiunii pentru a prelua datele din baza de date (parcurgerea tuturor datelor)

def rulare_completare_excel():

    sterge_tabele_excel()  # stergere pentru evitarea duplicatelor de fiecare data

    with SessionLocal() as s:
        toate = toate_pv(s)
        for pv in toate:

# TODO 9d: realizarea excelului caracteristic fiecarei saptamani - SITUATIA GENERALA DE LUCRARI 12-10-2026 - 16-10-2026.xlsx
#  -> excluderea zilei de duminica -> eroarea sa nu fie silentioasa
#  -> daca nu exista fisierul, il creeaza si se va completa in el, iar daca exista, se va completa in cel existent -> evitarea duplicatelor
#  -> folderul tuturor excelurilor va fi "exports"
#  -> MODEL.xlsx din folderul model_excel va fi copiat de fiecare data cand baza de date returneaza un element dintr-o saptamana noua
#  -> fisierul nou va fi redenumit conform modelului

            if pv.data.weekday() == 6:                                # nu trebuie sa exista zile de duminica -> zi libera
                print(f"PV {pv.id} nu a fost introdus din cauza datei de duminica")

            luni, sambata = inceput_final_saptamana(pv.data)  # preluarea primei si ultimei zi din saptamana

            TMP = "exports"
            os.makedirs(TMP, exist_ok=True)
            fisier_copiat = os.path.join("model_excel", "MODEL.xlsx")
            luni_convertit = luni.strftime("%d-%m-%Y")          # date(2026, 10, 12) -> 12-10-2026
            sambata_convertit = sambata.strftime("%d-%m-%Y")    # date(2026, 10, 16) -> 16-10-2026
            fisier_nou = os.path.join(TMP, f"SITUATIA GENERALA DE LUCRARI {luni_convertit} - {sambata_convertit}.xlsx")

            if not os.path.exists(fisier_nou):
                shutil.copy2(fisier_copiat, fisier_nou)   # copiaza modelul in fisierul_nou creat cu titlu unic
                print(f"S-a realizat fisierul {fisier_nou}")

# TODO 9e: stabilirea suprafetei de lucru: fisier caracteristic, ce foi se vor completa, redenumirea foilor
#  FISIERUL IN CARE SE COMPLETEAZA: -> daca se creeaza fisier nou -> workbook-ul va fi acel fisier - load_workbook()
#                                   -> daca exista deja -> se va parcurge calea fisierului saptamanii deja existente - load_workbook()
#  CE FOI TREBUIE COMPLETATE: -> de la foaia nr.4 -> index=3
#  REDENUMIREA FOILOR -> dupa pv.echipa (ex: Marius- Harghita)
#                     -> daca exista o foaie cu numele echipei -> se va lucra pe acea foaie
#                     -> daca nu, prima foaie nedenumita ("SHEET_GOL_1" - "SHEET_GOL_12") va primi numele echipei

            workbook = load_workbook(fisier_nou, keep_links=False)          # fisierul in care se va lucra -> keep_links=False taie legaturile cu modelul

            if pv.echipa in workbook.sheetnames:                            # alegerea foii unde se va completa
                foaie_echipa = workbook[pv.echipa]
            else:
                foaie_echipa = None
                for foaie in workbook.worksheets[3:]:                       # se va completa doar de la foaia 4 pana la 12
                    if foaie.title.startswith("SHEET_GOL_"):
                        foaie_echipa = foaie
                        foaie_echipa.title = pv.echipa
                        break

                if foaie_echipa is None:
                    raise ValueError(f"Nu mai exista foi pentru echipa {pv.echipa}")

# TODO 9f: completarea propriu-zisa in tabelele excel- completarea datelor
#  -> COMPLETAREA DATELOR -> in excel: D2 - I2 corespondent luni - sambata (parcurgere de 6 elemente)
#                         -> ziua introdusa este stabilita de functia de mai sus inceput_final_saptamana(data)
#                         -> stabiliraea coloanei datei din db -> luni = 0, marti = 1 ... sambata = 5 cf. data_pv.weekday()

            for index_zi in range(6):
                zi = luni + timedelta(days=index_zi)
                celula = foaie_echipa.cell(row=2, column=4 + index_zi)
                celula.value = zi

            coloana_zilei = 4 + pv.data.weekday()  # 4 corespunde coloanei D (de la D2 la I2 trebuie completata data)
            celula_zi = foaie_echipa.cell(row=2, column=coloana_zilei) # stabilirea celulei datei returnate de db

# TODO 9g: completarea propriu-zisa in tabelele excel- completarea cu valorile returnate de db in functie de cod
#   -> TABEL AJUTATOR - GRANITELE FIECARUI TABEL DIN ZIUA X
#   corelare_zile_tabele = {
#            "D2": ("C37", "D39-X63"),    # LUNI - C37 = D2 (ziua de luni), .... D39-X63 - tabelul corespondent zilei de luni
#            "E2": ("C70", "D71-X95"),    # MARTI - idem
#            "F2": ("C102","D103-X127"),  # MIERCURI - idem
#            "G2": ("C134","D135-X159"),  # JOI - idem
#            "H2": ("C166","D167-X191"),  # VINERI - idem
#            "I2": ("C198","D199-X223")   # SAMBATA - idem
#                          }
#   -> CONVERSIA TABELULUI PENTRU ACCESAREA VALORILOR (cu litere era nevoie de extragerea numerelor)
#   -> Preluarea granitelor tabelului -> din dictionar se coreleaza coordonatele zilei respective cu valorile implicite din tuplu
#   -> Definirea celulei unde sta codul: ex: A39, A40 .... A63
#   -> Definirea celulelor unde se vor trece valorile -> D39 - X39 .... D63 - X63 (D va avea coloana nr. 4 cf. excelului)
#   -> Daca, codul din  tabel corespunde cu cel din baza de date -> daca celula.value = None -> o completeaza
#                                                                -> altfel, trece la urmatoarea (pana la coloana X (24))

            corelare_zile_tabele = {
                "D2" : (39, 63),    # LUNI
                "E2" : (71, 95),    # MARTI
                "F2" : (103,127),   # MIERCURI
                "G2" : (135, 159),  # JOI
                "H2" : (167,191),   # VINERI
                "I2" : (199, 223)   # SAMBATA
            }

            coordonate_inceput, coordonate_final = corelare_zile_tabele[celula_zi.coordinate]

            valoare_scrisa = False

            for rand in range(coordonate_inceput, coordonate_final + 1):
                celula_cod = foaie_echipa.cell(row=rand, column=1)                            # Codul celulei din excel

                cod_fara_spatiu = "".join(str(celula_cod.value).split()).upper()              # normalizare cod "COP 1"

                if pv.cod == cod_fara_spatiu:
                    for coloana in range(4, 25):
                        celula_valoare = foaie_echipa.cell(row=rand, column=coloana)

                        if celula_valoare.value == 0:
                            celula_valoare.value = pv.valori
                            valoare_scrisa = True
                            break
                    break

            if not valoare_scrisa:
                print(f"valoarea {pv.valoare} al PV-ului {pv.id}- {pv.echipa} ({pv.data}) nu mai are loc in tabel")

# TODO 9h: SALVARE FISIER EXCEL

            workbook.save(fisier_nou)

### TESTARE
# rulare_completare_excel()























