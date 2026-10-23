
############################### PAGINA DE LISTARE/ FILTRARE ###############################

### IMPORTURI NECESARE

import streamlit as st
import pp5_comun

### TITLU PAGINA

st.title("📔📔📔 Lista Proceselor Verbale 📔📔📔")

### LEGATURA CU API -> raspuns api si preluarea proceselor verbale

ok, pv_uri = pp5_comun.api("GET", "/procese_verbale")

if not ok:
    st.error(pv_uri)
    st.stop()

if not pv_uri:
    st.info("Nu exista niciun proces verbal inca. Poti adauga cu ajutorul asistentului AI sau manual pe pagina 'Adauga un proces verbal'")
    st.stop()

### SIDEBAR: filtre (client-side) + total_km_echipa_zi si total_cod

CODURI = ["COP1", "COP2", "COP3", "COP4", "COP5","COP6", "COP8", "COP9", "COP10", "COP11", "COP12", "COP13", "COP14",
          "COP15", "COP16", "COP17", "COP18", "COP20", "COP21", "COP23", "COP24", "COP26", "COP27", "COP28", "COP29"]

with st.sidebar:

    st.sidebar.info("FILTRE - Cautare dupa echipa, cod, data")
    echipe_disponibile = sorted(list(set({pv["echipa"] for pv in pv_uri})))    # sortare alfabetica si eliminarea duplicatelor
    echipa_aleasa = st.sidebar.selectbox("ECHIPA", options=[None] + echipe_disponibile)
    cod_ales = st.sidebar.selectbox("COD", options=[None] + CODURI)
    data_aleasa = st.sidebar.date_input("DATA", None, key="Data_filtru")

    pv_filtrate = pv_uri

    if echipa_aleasa is None and cod_ales is None and data_aleasa is None:
        st.caption(f"Nu s-a aplicat niciun filtru: {len(pv_uri)} informatii totale")

    if echipa_aleasa is not None:
        pv_filtrate = [pv for pv in pv_filtrate if pv["echipa"] == echipa_aleasa]

    if cod_ales is not None:
        pv_filtrate = [pv for pv in pv_filtrate if pv["cod"] == cod_ales]

    # DATA TREBUIE CONVERTITA PENTRU COMPARAREA REZULTATELOR
    if data_aleasa is not None:
        pv_filtrate = [pv for pv in pv_filtrate if pv["data"] == data_aleasa.isoformat()]

    if not pv_filtrate:
        st.caption("Nu s-au gasit informatii conform filtrelor")
    else:
        st.caption(f"{len(pv_filtrate)} din {len(pv_uri)} informatii totale")

### LISTAREA sub forma unui tabel

st.dataframe(height="content", width="content", data=pv_filtrate)

# total_km_echipa_zi

with st.sidebar:

    st.info("TOTAL - Afla totalul parcurs de o echipa intr-o zi")

    with st.sidebar.form("Total_km", clear_on_submit=True):
        t_echipa_aleasa = st.selectbox("ECHIPA", options=echipe_disponibile)
        t_data_aleasa = st.date_input("DATA", "today", key="total_1")

        trimis = st.form_submit_button("Afla")

    if trimis:
        ok, total_km = pp5_comun.api("GET", "/total_km/echipa/data", params={"echipa": t_echipa_aleasa, "data": t_data_aleasa.isoformat()})

        if not ok:
            st.error(total_km)         # eroare API
            st.stop()

        if not total_km:               # total_km va fi 0 deoarece se iau in considerare doar anumite COP-uri,
            st.warning("Total: 0")     # functia din pp1_model (total_km) arunca o eroare cand nu exista procesul verbal

        else:
            st.warning(f"Total: {total_km}")

# total_cod

with st.sidebar:

    st.info("TOTAL - Afla totalul dupa cod")

    with st.form("Total_cod", clear_on_submit=True):
        s_echipa_aleasa = st.selectbox("ECHIPA", options=echipe_disponibile)
        s_cod_ales = st.selectbox("COD", options=CODURI)
        s_data_aleasa = st.date_input("DATA", key="total_2")

        trimis = st.form_submit_button("Afla")

    if trimis:

        ok, total_cod = pp5_comun.api("GET", "/total_cod/echipa/cod/data", params={"echipa": s_echipa_aleasa, "cod": s_cod_ales, "data": s_data_aleasa.isoformat()})

        if not ok:
            st.error(total_cod)         # eroare API
            st.stop()

        if not total_cod:
            st.warning("Nu exista informatia cautata")

        else:
            st.warning(f"Total: {total_cod}")

















