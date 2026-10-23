
############################### PAGINA DE ADAUGARE PROCES VERBAL ###############################

### IMPORTURI NECESARE

import streamlit as st
import pp5_comun
import pp8_procesator
from pp7_ocr import dictionar_coduri_valori
from pathlib import Path

### TITLU PAGINA

st.title("➕ Adauga un proces verbal ➕")

c1, c2 = st.columns(2)

### REALIZAREA UNUI FORMULAR + ADAUGARE PROPRIU-ZISA

with c1:

    st.info("1. Introdu manual informatii-> SALVARE")

    JUDETE = ["Alba", "Arad", "Arges", "Bacau", "Bihor", "Bistrita", "Botosani", "Braila", "Brasov","Buzau",
              "Calarasi", "Cluj", "Constanta", "Covasna", "Dambovita", "Dolj", "Galati","Giurgiu", "Gorj",
              "Harghita", "Hunedoara", "Ialomita", "Iasi", "Ilfov", "Maramures", "Mehedinti", "Mures", "Neamt", "Olt",
              "Prahova", "Salaj", "Satu Mare", "Severin", "Sibiu", "Suceava", "Teleorman", "Timis", "Tulcea", "Valcea", "Vaslui",
              "Vrancea", "Bucuresti"]

    CODURI = ["COP1", "COP2", "COP3", "COP4", "COP5","COP6", "COP8", "COP9", "COP10", "COP11", "COP12", "COP13", "COP14",
              "COP15", "COP16", "COP17", "COP18", "COP20", "COP21", "COP23", "COP24", "COP26", "COP27", "COP28", "COP29"]

    with st.form("Adauga date in procese verbale", clear_on_submit=True):
        nume_angajat_sef = st.text_input("Nume angajat-sef", placeholder="Introduceti un singur nume al angajatului-responsabil")
        judet = st.selectbox("Judet", options=JUDETE, placeholder="Alegeti un judet din Romania")
        echipa = nume_angajat_sef.strip().title() + "- " + judet
        cod = st.selectbox("Cod", options=CODURI, placeholder="Alegeti un cod")
        valori = st.number_input("Valoare", min_value=0.5, step=0.5, placeholder="Introduceti o valoare")
        data = st.date_input("Data", None)

        trimis = st.form_submit_button("Trimite")

    if trimis:
        ok, rezultat = pp5_comun.api("POST", "/adauga_procese_verbale", json={
            "echipa": echipa,
            "cod": cod,
            "valori": valori,
            "data": data.isoformat()
        })
        if ok:
            st.success(f"Informatie adaugata: {rezultat["id"]}.{rezultat["echipa"]} ({rezultat['data']})")
            st.dataframe(rezultat)
        else:
            st.error(rezultat)

### VARIANTA DE A ADAUGA O FOTOGRAFIE

# INFORMATII NOI: modulele pathlib si uuid
# pathlib -> lucrul cu fisierele si directoarele -> creeaza cai, foldere, subfoldere, fisiere cu format diferit
# uuid -> genereaza nume unice ale fisierelor

with c2:

    RADACINA_PROIECT = Path(__file__).resolve().parents[1]    #gaseste folderul si fisierul
                                                              #parents[1] este folderul proiect_personal_demo
                                                              #file este cel care ruleaza -> adauga.py
    FOLDER_PDF = RADACINA_PROIECT / "uploads"                #construieste folderul uploads
    FOLDER_PDF.mkdir(parents=True, exist_ok=True)            #creeaza folderul daca nu exista (exist_ok)
                                                              # il leaga de adauga.py (parents)

    st.info("2. Incarca un fisier .pdf -> CITIRE -> SALVARE")
    st.error("ATENTIE: Fisierele trebuie denumite UNIC, orice fisier cu denumire identica va fi PERMANENT INLOCUIT")

    with st.form("Incarca o fotografie cu un proces verbal"):
        pdf = st.file_uploader("Incarca un PV (format pdf, FORMAT OBLIGATORIU DENUMIRE: Angajat- Judet, Angjat2- Judet etc.)", type=["pdf"])
        data_poza = st.date_input("Data", "today")
        trimis = st.form_submit_button("Trimite")

    if trimis:
        if pdf is None:
            st.warning("Trebuie sa incarci un document pdf")
        else:

            nume_pdf = Path(pdf.name).name                   # preia numele original
            cale_pdf = FOLDER_PDF / nume_pdf                 # creeaza calea unde va fi salvata poza
            cale_pdf.write_bytes(pdf.getvalue())             # poza.getvalue() -> preia continutul imaginii sub forma de bytes
                                                             # .write_bytes() -> scrie continutul in folderul uploads

            st.success("Document trimis si salvat cu succes!")

# AFISAREA REZULTATELOR TRIMISE CATRE BAZA DE DATE

        rezultate = dictionar_coduri_valori()   # preia dictionarul din pp7_ocr -> {echipa1: {'cod': valoare, lista sau None, ...} ...}

        if rezultate is None:                                        # nu exista rezultate -> nu s-a citit nimic
            st.error("Nu exista date citite")
        elif nume_pdf not in rezultate:                              # nu exista numele in rezultate -> nu s-a citit nimic
            st.error(f"Nu exista date de citit pentru {nume_pdf}")
        else:
            rezultat_ultima_poza = rezultate[nume_pdf]               # preia doar numele ultimei poze introduse
            valori_afisate = []
            st.info(f"A fost adaugata echipa {nume_pdf} ({data})")
            for cod, valoare in rezultat_ultima_poza.items():        # parcurge datele
                if valoare is None:
                    continue
                if isinstance(valoare, list):                        # [1, 2, 3] -> '1, 2, 3' (str pentru afisare)
                    valoare_afisata = ",".join(str(element) for element in valoare)
                else:
                    valoare_afisata = str(valoare)                   # 2 -> '2' (str pentru afisare)
                valori_afisate.append(f"{cod} = {valoare_afisata}")  # adaugarea unui mesaj intr-o lista ce va fi afisata
        with st.expander("AFISEAZA VALORILE CITITE"):
            if valori_afisate:                                       # exista valori afisate -> afiseaza-le
                st.write(valori_afisate)
            else:                                                    # altfel, OCR-ul nu a identificat text
                st.warning("OCR-ul nu a identificat text")

        try:
            nr_inreg = pp8_procesator.adaugare_db_poze(nume_pdf, data_poza)   # incearca sa validezi datele
            st.success(f"Au fost adaugate {nr_inreg} in baza de date")        # afiseaza nr. celor adaugate
        except Exception as e:                                                # altfel, afiseaza eroarea
            st.error(f"Datele nu au fost adaugate: {e}")

### AFISARE INSTRUCTIUNI IN SIDEBAR

with st.sidebar:

    with st.container(border= True):
        st.warning("INSTRUCTIUNI DE UTILIZARE")

        st.info("1. Introdu manual informatii")
        st.caption("a. Introduceti un nume al angajatului (un singur cuvant- nume, prenume, porecla etc.)")
        st.caption("b. Alegeti un judet => programul va genera automat un nume al echipei pe formatul Nume- Judet")
        st.caption("c. Alegeti un cod din lista (asociat cu descrierea din sablon)")
        st.caption("d. Introduceti o valoare ex. 10.50 sau 10")
        st.caption("e. Alegeti o data din calendar")
        st.caption("f. Adaugarea se va face doar dupa apasarea butonului 'Trimite'")

        st.info("2. Incarca un fisier .jpg, .jpeg sau .png")
        st.caption("a. Atasati un fisier pentru citire si salvare in baza de date")
        st.caption("b. Incarcarea se va face doar dupa apasarea butonului 'Trimite'")

        st.info("3. Ataseaza un link de invitatie pentru a prelua imaginile")
        st.caption("a. Atasati un link cu grupul de whatsapp de unde vor fi preluate pozele si salvate")
        st.caption("b. Accesarea se va face doar dupa apasarea butonului 'Trimite'")

        st.caption("")
        st.caption("Orice valoare introdusa incorect va fi semnalizata in interfata")


















