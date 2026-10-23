
############################### PROCESATOR IN BAZA DE DATE ###############################

### IMPORTURI NECESARE

from pathlib import Path
import pp1_model
from pp1_model import SessionLocal
from pp2_schema import PvIn
from pp7_ocr import dictionar_coduri_valori

# ###################################################################################################################
# PARTEA 8A - PROCESATOR DATE IMAGINI- validarea si constructia datelor citite de ocr + adaugarea in baza de date
# ###################################################################################################################

# TODO 8A: functia adaugare_db_poze(nume_pdf, data) -> numele echipei si data vor fi luate din Streamlit
#  -> preluarea rezultatului returnat de pp7_ocr -> dictionar_coduri_valori() -> {echipa1: {'cod': valoare, lista sau None, ...} ...}
#  -> realizarea unui obiect cu elementele (echipa, cod, valoare, data) -> echipa - numele fisierului, preluat din Streamlit
#                                                                       -> cod - fiecare cod al fiecarei echipe
#                                                                       -> valoare - fiecare valoare a fiecarui cod
#                                                                       -> data - introdusa in Streamlit
#  -> validarea datei -> daca e duminica -> eroare
#  -> punerea fiecarei valori in lista (unele sunt deja in lista daca sunt mai multe, altele sunt float-uri)
#  -> validarea obiectului cu PvIn(...)
#  -> realizarea si completarea unei liste cu datele inregistrate
#  -> deschiderea sesiunii si adaugarea datelor
#  -> returnarea lungimii inregistrarilor - pentru Streamlit

def adaugare_db_poze(nume_pdf, data):

    rezultate = dictionar_coduri_valori()  # returneaza dictionarul din pp7_ocr => {echipa1: {'cod': valoare, lista sau None, ...} ...}

    if rezultate is None:                  # daca nu gaseste -> nu exista
        raise ValueError("Nu există rezultate OCR.")

    cheie_pdf = Path(nume_pdf).name        # preia numele caii imaginii cu tot cu extensie eliminand numele directoarelor

    if cheie_pdf not in rezultate:         # nu exista -> nu exista numele
        raise ValueError(f"Nu există rezultate OCR pentru {cheie_pdf}.")

    echipa = Path(cheie_pdf).stem          # preia numele fara terminatia .pdf

    if data.weekday() == 6:                # daca ziua pica duminica -> eroare (nu se lucreaza duminica)
        raise ValueError(
            f"PV {echipa} ({data}) nu poate fi introdus deoarece data este duminică.")

    rezultat_pdf = rezultate[cheie_pdf]    # preia un element din dictionarul returnat de pp7_ocr

    inregistrari_validate = []             # lista cu viitoarele date validate

    for cod, valoare in rezultat_pdf.items():   # parcurgerea fiecarui element (echipa si codurile/valorile aferente)
        if valoare is None:                     # nu exista valoare -> trece mai departe
            continue

        if isinstance(valoare, list):           # daca valoarea este o lista -> o preia pur si simplu
            valori = valoare
        else:                                   # daca valoarea este un float -> il pune in lista
            valori = [valoare]

        for element in valori:                  # validarea fiecarui element din lista -> trecerea in lista
            pv_validat = PvIn(echipa=echipa, cod=cod, valori=float(element),data=data)
            inregistrari_validate.append(pv_validat)

    if not inregistrari_validate:               # lista goala -> nu s-a citit/validat nimic
        raise ValueError(f"Nu există valori de introdus pentru {cheie_pdf}.")

    with SessionLocal() as db:                  # deschiderea unei sesiuni -> adaugarea noilor randuri din PV
        for pv in inregistrari_validate:
            pp1_model.adauga_pv(db, echipa=pv.echipa, cod=pv.cod.value, valori=pv.valori, data=pv.data)

    return len(inregistrari_validate)           # returnarea lungimii inregistrarilor validate -> afisare in Streamlit





























