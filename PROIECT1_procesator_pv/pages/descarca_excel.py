
############################### PAGINA DESCARCA EXCEL-URI ###############################

# Alegerea din documentele excel din exports a celui pe care utilizatorul doreste sa o descarce

### IMPORTURI NECESARE

from pathlib import Path
import streamlit as st
import pp9_excel

# GENERAREA DOCUMENTELOR EXCEL ACTUALIZATE - apelarea functiei rulare_completare_excel() din pp9_excel
#                                          - realizarea unui spinner pentru a informa utilizatorul ca se incarca

c1, c2, c3 = st.columns(3)

with c2:

    st.subheader("Apasa pentru a genera documentele Excel actualizate")

    if st.button("Genereaza EXCEL"):
        try:
            with st.spinner("Se generează documentele Excel..."):
                pp9_excel.rulare_completare_excel()
            st.success("Documentele Excel au fost generate cu succes!")
        except Exception as eroare:
            st.error("Documentele nu au putut fi generate.")
            st.exception(eroare)

# CREAREA CAILOR CATRE FISIERE SI VERIFICAREA DATELOR (sa fie fisier, sa fie excel, sa existe)

    folder_exports = Path(__file__).resolve().parent.parent / "exports"
    extensii_excel = {".xlsx", ".xls", ".xlsm"}

    fisiere_excel = []

    for fisier in folder_exports.iterdir():
        if fisier.is_file() and fisier.suffix.lower() in extensii_excel:
            fisiere_excel.append(fisier)

    if not fisiere_excel:
        st.info("Nu există fișiere Excel în folderul exports.")

# DACA TRECE DE VALIDARI -> afiseaza in selectbox variantele -> cea selectata se va descarca

    else:
        st.write('*************************************************************************')
        st.subheader("DESCARCA SITUATIA GENERALA DE LUCRARI")

        with st.container(border=True):

            fisier_selectat = st.selectbox("Alege fișierul pe care vrei sa il descarci", options=fisiere_excel, format_func=lambda fisier: fisier.name)

            if fisier_selectat.suffix.lower() == ".xlsx":
                mime = ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") # pentru acceptarea formatului
            elif fisier_selectat.suffix.lower() == ".xlsm":
                mime = "application/vnd.ms-excel.sheet.macroEnabled.12"                      # pentru acceptarea formatului
            else:
                mime = "application/vnd.ms-excel"

            if st.download_button(label="Descarca", data=fisier_selectat.read_bytes(), file_name=fisier_selectat.name,
                                  mime=mime, key="buton_descarcare_excel"):
                st.balloons()
                st.success(f"{fisier_selectat.name} a fost descarcat cu succes!")


with st.sidebar:

    with st.container(border= True):
        st.warning("INSTRUCTIUNI DE UTILIZARE")

        st.info("Utilizarea PAGINII DE GENERARE SI DESCARCARE A SITUATIEI GENERALE")
        st.caption("1. Sectiunea de GENERARE")
        st.caption("a. Apasati butonul 'Genereaza EXCEL' pentru a genera TOATE documentele Excel ACTUALIZATE")
        st.caption("2. Sectiunea de DESCARCARE")
        st.caption("a. Selectati documentul Excel din saptamana pe care doriti sa o descarcati")
        st.caption("b. Apasati butonul 'Descarca' pentru a descarca documentul selectat")












