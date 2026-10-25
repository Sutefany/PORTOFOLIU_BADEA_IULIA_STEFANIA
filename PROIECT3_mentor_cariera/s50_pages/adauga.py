import streamlit as st
from comun import api

st.title("➕ Adauga ghid")
st.caption("La salvare, ghidul intra si in indexul RAG - mentorul il poate folosi imediat.")

with st.form("form_ghid_nou", clear_on_submit=True):
    c1, c2 = st.columns([3, 1])
    titlu = c1.text_input("Titlu", placeholder="ex: Scrisoarea de intentie")
    categorie = c2.selectbox("Categorie", ["CV si portofoliu", "Interviu", "Negociere",
                                           "Roluri IT", "La job", "Altele"])
    continut = st.text_area("Continut", height=300,
                            placeholder="Scrisoarea de intentie explica de ce te potrivesti pentru rol...")

    trimis = st.form_submit_button("Adauga", type="primary")

if trimis:
    ok, rezultat = api("POST", "/ghiduri", json={
        "titlu": titlu,
        "categorie": categorie,
        "continut": continut,
    }, timeout=30)

    if ok:
        st.success(f"{titlu} adaugat")
    else:
        st.error(rezultat)
