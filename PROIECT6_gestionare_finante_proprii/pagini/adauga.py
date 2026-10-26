from datetime import date

import streamlit as st
from comun import api

st.title("➕ Adauga tranzactie")

CATEGORII = {
    "venit": ["salariu", "freelance", "alt venit"],
    "cheltuiala": ["mancare", "locuinta", "transport", "facturi", "distractie", "sanatate", "altele"],
}


tip = st.radio("Tip", ["cheltuiala", "venit"], horizontal=True)

with st.form("form_tranzactie_noua", clear_on_submit=True):
    descriere = st.text_input("Descriere", placeholder="ex: Cumparaturi Lidl")

    c1, c2, c3 = st.columns(3)
    categorie = c1.selectbox("Categorie", CATEGORII[tip])
    suma = c2.number_input("Suma (lei)", min_value=0.0, step=10.0, value=100.0)
    data = c3.date_input("Data", value=date.today())

    trimis = st.form_submit_button("Adauga", type="primary")

if trimis:
    ok, rezultat = api("POST", "/tranzactii", json={
        "descriere": descriere,
        "tip": tip,
        "categorie": categorie,
        "suma": suma,
        "data": data.isoformat(),
    })
    if ok:
        st.success(f"Adaugat: {rezultat['descriere']} ({rezultat['tip']}, {rezultat['suma']:,.0f} lei)")
    else:
        st.error(rezultat)
