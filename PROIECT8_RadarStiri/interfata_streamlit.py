# =============================================================================================
# MINI-PROIECT: "Radar Biziday"  (Web Scraping) - Punerea informatiilor in interfata Streamlit
# =============================================================================================

# Scop:
# Filtrare pe categorii: sport, sanatate, politica, educatie, vreme etc. - specificare doar
# Filtrare pe categorii: locatie (european, local etc.) - specificare doar
# Filtrare dupa cauza si efect: pozitiv, negativ, neutru - specificare doar
# Realizarea unor statistici dupa categorii (grafice sugestive) - grafic sintetizator (aici se vede ponderea de fapt)
# Realizarea unui RAPORT ZILNIC

import streamlit as st
from  procesator_stiri import stiri_de_pe_pagina, sursa_cea_mai_frecventa, URL
from agent import ruleaza_agent
from agent import CATEGORII_CLASICE, EFECT, LOCATIE

st.set_page_config(page_title="PROCESATOR STIRI", page_icon="🚓", layout="centered")

st.title("🚓🚑🚨 RADAR DE STIRI 🚓🚑🚨")

with st.sidebar:
    st.subheader("RADAR BIZIDAY - sinteza stirilor de ultima ora")
    with st.container(border=True):
        st.warning("INSTRUCTIUNI DE UTILIZARE")
        st.caption("1. Alegeti cate stiri vreti sa va fie sintetizate (min. 1, max. 20)")
        st.caption("2. Se prezinta sinteza, categoriile aferente, data si sursa stirii")
        st.caption("3. Mai jos se vor genera graficele aferente categoriilor mentionate")

if "stiri" not in st.session_state:
    st.session_state.stiri= []

if "clasificari" not in st.session_state:
    st.session_state.clasificari= []

if "apeluri" not in st.session_state:
    st.session_state.apeluri= []

with st.container(border=True):
    with st.form("Alegeti numarul celor mai recente stiri pe care doriti sa il aflati"):
        nr = st.slider("Numarul stirilor", min_value=1, max_value=20, step=1, value=5)
        trimis = st.form_submit_button("Afiseaza stirile")
    if trimis:
        try:
            toate_stirile = stiri_de_pe_pagina(URL)

            if not toate_stirile:
                st.warning("Nu exista stiri")
                st.stop()

            stiri_selectate = toate_stirile[:nr]

            clasificari = []
            toate_apelurile = []

            with st.spinner("Stirile sunt analizate..."):
                for stire in stiri_selectate:
                    clasificare, apeluri = ruleaza_agent(mesaj=stire["text"], istoric=[])
                    clasificari.append(clasificare)
                    toate_apelurile += apeluri

            st.session_state.stiri = stiri_selectate
            st.session_state.clasificari = clasificari
            st.session_state.apeluri = toate_apelurile

        except Exception as e:
            st.error(f"Ceva nu a functionat: {e}")

    if st.session_state.stiri:
        stiri = st.session_state.stiri
        clasificari = st.session_state.clasificari
        sursa_frecventa = sursa_cea_mai_frecventa(stiri)
        if sursa_frecventa:
            if sursa_frecventa:
                st.info(f"SURSA CEA MAI FRECVENTA: {sursa_frecventa[0]} -> {sursa_frecventa[1]}")

        st.subheader(f"Ultimele {len(stiri)} stiri")
        for index, stire in enumerate(stiri):
            clasificare = clasificari[index]

            with st.expander(f"STIREA NR. {index + 1}"):
                st.caption(
                    f"CATEGORIA: :red[{clasificare['categorie']}] | "
                    f"EFECT: :red[{clasificare['efect']}] | "
                    f"LOCATIA: :red[{clasificare['locatie']}]")

                st.write(f":blue[CONTINUT]: {stire['text']}")
                st.write(f":green[DATA]: {stire['data']} {stire['ora']}")
                st.warning(f"SURSA: {stire['url']} ({stire['sursa']})")


        with st.sidebar:

            st.info("GRAFIC CATEGORII CLASICE (sport, politica etc.)")

            with st.expander("Sinteza grafica a stirilor pe categorii"):

                procente_categorii = []

                for categorie in CATEGORII_CLASICE:
                    numar = 0
                    for clasificare in clasificari:
                        if clasificare['categorie'] == categorie:
                            numar += 1
                    procent = numar * 100 / len(clasificari)
                    procente_categorii.append(procent)

                date_categorii = {
                    "Categorie": CATEGORII_CLASICE,
                    "Procent": procente_categorii
                }

                st.bar_chart(date_categorii, x="Categorie", y="Procent", x_label="Categorii", y_label="Procent(%)")

            st.info("GRAFIC EFECTE (posizitiv, neutru, negativ)")

            with st.expander("Sinteza grafica a stirilor pe efecte"):

                procente_efecte = []

                for e in EFECT:
                    numar = 0
                    for clasificare in clasificari:
                        if clasificare['efect'] == e:
                            numar += 1
                    procent = numar * 100 / len(clasificari)
                    procente_efecte.append(procent)

                date_efecte = {
                    "Efect": EFECT,
                    "Procent": procente_efecte
                }

                st.bar_chart(date_efecte, x="Efect", y="Procent", x_label="Efect", y_label="Procent(%)")

            st.info("GRAFIC ARIE GEOGRAFICA DE AFECTARE (national, european, mondial)")

            with st.expander("Sinteza grafica a stirilor pe locatie"):

                procente_loc = []

                for l in LOCATIE:
                    numar = 0
                    for clasificare in clasificari:
                        if clasificare['locatie'] == l:
                            numar += 1
                    procent = numar * 100 / len(clasificari)
                    procente_loc.append(procent)

                date_locatie = {
                    "Locatie": LOCATIE,
                    "Procent": procente_loc
                }

                st.bar_chart(date_locatie, x="Locatie", y="Procent", x_label="Locatie", y_label="Procent(%)")








