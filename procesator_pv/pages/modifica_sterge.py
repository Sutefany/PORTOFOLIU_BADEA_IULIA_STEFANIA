
############################### PAGINA DE MODIFICARE/ STERGERE PROCESE VERBALE ###############################

import streamlit as st
import pp5_comun
from datetime import date

### TITLU PAGINA

st.title("✒️✒️✒️ Modifica/Sterge date ✒️✒️✒️")

c1, c2, c3 = st.columns(3)

### REALIZAREA UNUI FORMULAR + MODIFICARI PROPRIU-ZISE

with c1:

    st.info("1. Modifica manual informatii-> SALVARE")

    ok, pv_uri = pp5_comun.api("GET", "/procese_verbale")

    if not ok:
        st.error(pv_uri)
        st.stop()

    if not pv_uri:
        st.info("Nu exista niciun proces verbal inca. Poti adauga cu ajutorul asistentului AI sau manual pe pagina 'Adauga un proces verbal'")
        st.stop()

    toate_id = [nr["id"] for nr in pv_uri]

    CODURI = ["COP1", "COP2", "COP3", "COP4", "COP5","COP6", "COP8", "COP9", "COP10", "COP11", "COP12", "COP13", "COP14",
              "COP15", "COP16", "COP17", "COP18", "COP20", "COP21", "COP23", "COP24", "COP26", "COP27", "COP28", "COP29"]

    pv_id = st.selectbox("OBLIGATORIU: Cauta dupa ID", options=sorted(toate_id))

    pv_gasit = None

    for pv in pv_uri:
        if pv["id"] == pv_id:
            pv_gasit = pv
            break

    if pv_gasit is None:
        st.error(f"Nu exista pv-ul cu id-ul {pv_id}")
        st.stop()
    else:
        st.success(f"Elementul cu id-ul {pv_id} a fost gasit!")

    data_initiala = date.fromisoformat(pv_gasit["data"][:10]) # "2026-10-12" -> date(2026, 10, 12) -> "2026-10-12T14:30:00" -> 2026-10-12

    with st.form("Modifica datele unui proces verbal - Date default ce pot fi modificate"):
        echipa_noua = st.text_input("OPTIONAL: Introduceti o echipa noua", value=str(pv_gasit["echipa"] or None))
        cod_nou = st.selectbox("OPTIONAL: Alegeti un cod nou", options=CODURI, index=CODURI.index(pv_gasit["cod"]))
        valoare_noua = st.number_input("OPTIONAL: Introduceti o valoare noua", min_value=0.5, step=0.5, value=pv_gasit["valori"])
        data = st.date_input("OPTIONAL: Alegeti o data noua", value=data_initiala, key=f"data_modificare{pv_id}")  # un key fix nu lasa sa modifice data

        trimis = st.form_submit_button("Trimite")

    if trimis:
        ok, rezultat = pp5_comun.api("PUT", f"/modifica_proces_verbal/{pv_id}", json={
            "echipa": echipa_noua,
            "cod": cod_nou,
            "data": data.isoformat(),
            "valori": valoare_noua})
        if ok:
            st.success(f"Informatie modificata: {rezultat['id']}.{rezultat['echipa']} ({rezultat['data']})")
        else:
            st.error(rezultat)

### REALIZAREA UNUI FORMULAR + STERGE UN PROCES VERBAL INTREG PE O ZI AL UNEI ECHIPE

with c2:

    st.info("2. Sterge manual informatii (TOT PV-UL)-> SALVARE")

    with st.form("Sterge un proces verbal", clear_on_submit=True):
        echipa = st.selectbox("Alege echipa", options=sorted(list(set([pv["echipa"] for pv in pv_uri]))))
        data = st.date_input("Data", value="today", key="data")

        sterge = st.form_submit_button("Sterge")

    if sterge:
        ok, rezultat = pp5_comun.api("DELETE", f"/sterge_proces_verbal/{echipa}/{data.isoformat()}")

        if ok:
            st.success(f"PV sters: {echipa} - {data}")
        else:
            st.error(rezultat)

### REALIZAREA UNUI FORMULAR + STERGE DINTR-UN PROCES VERBAL UN RAND (DUPA ID)

with c3:

    st.info("3. Sterge manual informatii (DOAR O INFORMATIE)-> SALVARE")

    optiuni = []

    for rand in pv_uri:
        optiuni.append(f"{rand["id"]}. {rand['echipa']} ({rand["data"]}) - {rand["cod"]} => {rand["valori"]}")

    id_existente = [pv["id"] for pv in pv_uri]
    echipe_existente = [pv["echipa"] for pv in pv_uri]
    cod = [pv["cod"] for pv in pv_uri]
    data = [pv["data"] for pv in pv_uri]

    with st.form("Sterge un rand dupa ID", clear_on_submit=True):
        id = st.selectbox("Alege randul de sters", options=sorted(id_existente))
        st.subheader("Optiuni de stergere")
        st.dataframe(data = optiuni)

        sterge = st.form_submit_button("Sterge")

        if sterge:
            ok, rezultat = pp5_comun.api("DELETE", f"/sterge_pv/{id}")

            if ok:
                st.success(f"PV sters: {id}")
            else:
                st.error(rezultat)

    if st.button("Apasa aici pentru a viziona tabelul modificat"):
        st.rerun()

### AFISARE INSTRUCTIUNI IN SIDEBAR

with st.sidebar:

    with st.container(border= True):
        st.warning("INSTRUCTIUNI DE UTILIZARE")

        st.info("1. Modifica manual informatii")
        st.caption("a. Alege un id din lista de id-uri valabile")
        st.caption("b. Tabelul va genera automat valorile implicite ale randului cu id-ul cerut")
        st.caption("c. OPTIONAL: Modificati numele echipei (FFORMAT OBLIGATORIU: Nume- Judet)")
        st.caption("d. OPTIONAL: Alegeti un cod nou")
        st.caption("f. OPTIONAL: Introduceti o valoare noua ex. 10.50 sau 10")
        st.caption("e. OPTIONAL: Alegeti o data noua din calendar")
        st.caption("f. Modificarea se va face doar dupa apasarea butonului 'Trimite'")

        st.info("2. Sterge manual informatii (TOT PV-UL)")
        st.caption("a. Alegeti echipa din lista de echipe existente")
        st.caption("b. Selectati data in care a lucrat echipa")
        st.caption("c. Stergerea se va face doar dupa apasarea butonului 'Sterge'")

        st.info("3. Sterge manual informatii (DOAR O INFORMATIE)-> SALVARE")
        st.caption("a. Alegeti id-ul elementului pe care vreti sa il stergeti")
        st.caption("b. Stergerea se va face doar dupa apasarea butonului 'Sterge'")

        st.caption("")
        st.caption("Orice valoare introdusa incorect va fi semnalizata in interfata")
