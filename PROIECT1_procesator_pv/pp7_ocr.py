
############################### CITIRE PDF-URI CU RapidOCR ###############################

### IMPORTURI NECESARE

import re
from pathlib import Path
from pprint import pprint
import cv2
import numpy as np
import pymupdf
from rapidocr import RapidOCR, LangRec

# ###################################################################################
# PARTEA 7A - LEGATURA CU FOLDERUL IMPLICIT + SABLOANE + pornirea OCR-ului LOCAL
# ###################################################################################

# TODO 7a: crearea unei cai catre folderul "uploads" unde se afla pdf-urile salvate

FOLDER_COD = Path(__file__).resolve().parent
FOLDER_PDF = FOLDER_COD / "uploads"

# TODO 7b: listarea codurilor -> viitor sablon

CODURI = ["COP1", "COP2", "COP3", "COP4", "COP5", "COP6", "COP8", "COP9", "COP10", "COP11", "COP12", "COP13", "COP14",
          "COP15", "COP16", "COP17", "COP18", "COP20", "COP21", "COP23", "COP24", "COP26", "COP27", "COP28", "COP29"]

# TODO 7c: stabilirea coordonatelor tabelului

# FOAIE: 150 DPI, 2290 x 3200 (LATIME_REFERINTA- LUNGIME_REFERINTA)
# X_REFERINTA = inceputul si finitul fiecarei casute (COLOANELE)
# Y_REFERINTA = inceputul si finitul fiecarei casute (RANDURILE)

LATIME_REFERINTA = 2290
INALTIME_REFERINTA = 3200

X_REFERINTA = [242, 382, 517, 652, 786, 920, 1052, 1180, 1313, 1445, 1578, 1712, 1849, 1983, 2116, 2254]

Y_REFERINTA = [722, 785, 849, 911, 974, 1036, 1099, 1161, 1226, 1288, 1350, 1412, 1475, 1537, 1600, 1662, 1725, 1786,
               1848, 1910, 1974, 2037,2100, 2162, 2225, 2288]

# TODO 7d: pornirea RapidOCR local

ocr = RapidOCR(params={"Rec.lang_type": LangRec.EN, "Global.text_score": 0.0, "Global.log_level": "error"})

# ######################################################################################################################
# PARTEA 7B - PREGATIREA PENTRU OCR - transformare pdf in imagine, pixeli albastri in casuta <=> completat, aranjarea celulei
# ######################################################################################################################

# TODO 7e: transformarea pdf-ului in imagine

def pdf_in_imagine(cale_pdf):
    document = pymupdf.open(cale_pdf)

    if document.page_count == 0:
        document.close()
        raise ValueError("PDF-ul nu conține nicio pagină.")

    pagina = document[0]
    pixmap = pagina.get_pixmap(dpi=150, alpha=False)
    imagine_rgb = np.frombuffer(pixmap.samples,dtype=np.uint8).reshape(pixmap.height,pixmap.width,pixmap.n)
    document.close()
    imagine_bgr = cv2.cvtColor(imagine_rgb, cv2.COLOR_RGB2BGR)   # accepta doar format bgr
    return imagine_bgr

# TODO 7f: extragerea scrisului albastru -> COMPLETARE OBLIGATORIE CU PIX ALBASTRU

def extrage_masca_albastra(celula):
    hsv = cv2.cvtColor(celula, cv2.COLOR_BGR2HSV)
    limita_minima = np.array([90, 35, 0])           # limite pentru culoarea albastra (min.)
    limita_maxima = np.array([145, 255, 220])       # limite pentru culoarea albastra (max.)
    masca = cv2.inRange(hsv,limita_minima,limita_maxima)
    return masca

# TODO 7g: decuparea celulei completate

def celula_este_completata(celula):
    masca = extrage_masca_albastra(celula)
    numar_pixeli = cv2.countNonZero(masca)
    return numar_pixeli >= 300

# TODO 7h: pregatirea celulei -> marire, masca alba pentru a evita confuzia cu marginile celulei

def pregateste_celula(celula):
    celula_marita = cv2.resize(celula,None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    celula_marita = cv2.copyMakeBorder(celula_marita, 25, 25, 25, 25, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    return celula_marita

# ###################################################################################
# PARTEA 7C - CITIRE - o celula, un tabel
# ###################################################################################

# TODO 7i: citirea unei celule

def citeste_celula(celula):
    imagine_ocr = pregateste_celula(celula)
    rezultat = ocr(imagine_ocr, use_det=False, use_cls=False, use_rec=True)
    texte = getattr(rezultat, "txts", None)
    scoruri = getattr(rezultat, "scores", None)

    if not texte:
        return None, 0.0

    text = "".join(str(element) for element in texte)
    cifre = re.sub(r"[^0-9]", "", text) # pastreaza doar cifrele

    if not cifre:
        return None, 0.0

    if scoruri is not None and len(scoruri) > 0:
        incredere = float(max(scoruri))
    else:
        incredere = 0.0

    return cifre, incredere

# TODO 7j: citirea tabelului intreg

def citeste_tabel_pdf(cale_pdf):
    imagine = pdf_in_imagine(cale_pdf)
    inaltime, latime = imagine.shape[:2]
    coordonate_x = [round(x / LATIME_REFERINTA * latime) for x in X_REFERINTA]
    coordonate_y = [round(y / INALTIME_REFERINTA * inaltime) for y in Y_REFERINTA]

    rezultat_final = {cod: None for cod in CODURI}        #dictionar-sablon - fiecare cod: None -> completare ulterioara

    diagnostic = []

    for indice_rand, cod in enumerate(CODURI):
        y1 = coordonate_y[indice_rand]
        y2 = coordonate_y[indice_rand + 1]

        valori_rand = []

        for indice_coloana in range(len(coordonate_x) - 1):
            x1 = coordonate_x[indice_coloana]
            x2 = coordonate_x[indice_coloana + 1]

            margine_x = max(4, round((x2 - x1) * 0.04))  # eliminarea liniilor fiecarei casute
            margine_y = max(4, round((y2 - y1) * 0.08))  # eliminarea liniilor fiecarei casute

            celula = imagine[y1 + margine_y:y2 - margine_y,x1 + margine_x:x2 - margine_x]

            if celula.size == 0:
                continue

            if not celula_este_completata(celula):       # celula necompletata (fara albastru) nu va apela OCR-ul
                continue

            valoare, incredere = citeste_celula(celula)

            diagnostic.append({
                "cod": cod,
                "coloana": indice_coloana + 1,
                "valoare": valoare,
                "incredere": round(incredere, 3)
            })

            if valoare is not None:
                valori_rand.append((indice_coloana,valoare))

        valori_rand.sort(key=lambda element: element[0])  # valori pastrate in ordinea coloanelor
        valori = [valoare for _, valoare in valori_rand]

        if len(valori) == 1:
            rezultat_final[cod] = valori[0]

        elif len(valori) > 1:
            rezultat_final[cod] = valori

    return rezultat_final, diagnostic

# ###################################################################################
# PARTEA 7D - PROGRAMUL PRINCIPAL
# ###################################################################################

# TODO 7K: aranjarea datelor sub forma unui dictionar cu echipa, codurile si valorile
#  functia  dictionar_coduri_valori() -
#  OUTPUT dorit: {NumeEchipa: {COD: valoare, lista sau None, COD: valoare, lista sau None ....}, ....}
#       exemplu: {"Popescu-Arges": {"COP1": 23,"COP2": None, "COP3": [12, 13, 14], .... , "COP29": None}, ....}

def dictionar_coduri_valori():
    if not FOLDER_PDF.exists():
        print(f"Folderul nu există: {FOLDER_PDF}")
        print("Creez folderul automat...")
        FOLDER_PDF.mkdir(parents=True, exist_ok=True)  # face legatura dintre foldere

        print("Pune PDF-urile în acest folder și rulează din nou programul.")
        return

    fisiere_pdf = sorted(FOLDER_PDF.glob("*.pdf"))    # preia fisierele la apelare (generator)

    if not fisiere_pdf:                               # nu exista -> Nu exista PDF-uri
        print(f"Nu există PDF-uri în folderul: {FOLDER_PDF}")
        return

    rezultate_toate_pdf_urile = {}                    # punerea tuturor rezultatelor intr-un dictionar

    for cale_pdf in fisiere_pdf:                      # afisare a numelui cu print
        print("\n" + "=" * 60)
        print(f"PDF: {cale_pdf.name}")
        print("=" * 60)
        try:
            rezultat, diagnostic = citeste_tabel_pdf(cale_pdf)
            rezultate_toate_pdf_urile[cale_pdf.name] = rezultat
            print("\nDicționarul rezultat:")
            pprint(rezultat, sort_dicts=False)
            print("\nDiagnostic OCR:")
            for element in diagnostic:
                print(
                    f"{element['cod']}, "
                    f"coloana {element['coloana']}: "
                    f"{element['valoare']} "
                    f"(încredere {element['incredere']})"
                )
        except Exception as eroare:
            print(f"Eroare la {cale_pdf.name}: {eroare}")

    print("\n" + "=" * 60)
    print("REZULTATELE TUTUROR PDF-URILOR")
    print("=" * 60)

    pprint(rezultate_toate_pdf_urile, sort_dicts=False)
    return rezultate_toate_pdf_urile


## TESTARE FUNCTIONALITATE
# print(dictionar_coduri_valori())

# OUTPUT:
# {'Popescu- Bacau.pdf': {'COP1': '5',
#                         'COP2': '3',
#                         'COP3': None,
#                         'COP4': None,
#                         'COP5': None,
#                         'COP6': '35',
#                         'COP8': ['80', '100', '60'],
#                         'COP9': None,
#                         'COP10': None,
#                         'COP11': ['1200', '360', '231'],
#                         'COP12': None,
#                         'COP13': None,
#                         'COP14': None,
#                         'COP15': '1',
#                         'COP16': None,
#                         'COP17': None,
#                         'COP18': None,
#                         'COP20': ['550', '230'],
#                         'COP21': None,
#                         'COP23': '2',
#                         'COP24': '8',
#                         'COP26': ['6', '8'],
#                         'COP27': None,
#                         'COP28': None,
#                         'COP29': None}}
