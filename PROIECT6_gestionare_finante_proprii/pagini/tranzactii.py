from datetime import date

import streamlit as st
from comun import api

st.title("💸 Tranzactii")

st.sidebar.header("Filtre")
luna = st.sidebar.text_input("Luna (YYYY-MM)", value=date.today().strftime("%Y-%m"))
tip = st.sidebar.selectbox("Tip", ["Toate", "venit", "cheltuiala"])

params = {}
if luna:
    params["luna"] = luna
if tip != "Toate":
    params["tip"] = tip

ok, tranzactii = api("GET", "/tranzactii", params=params)
if not ok:
    st.error(tranzactii)
    st.stop()

if not tranzactii:
    st.info("Nicio tranzactie pentru filtrele alese. Adauga una din 'Adauga tranzactie' "
            "sau spune-i Consilierului AI.")
    st.stop()

venituri = 0
cheltuieli = 0

for t in tranzactii:
    if t["tip"] == "venit":
        venituri = venituri + t["suma"]
    else:
        cheltuieli = cheltuieli + t["suma"]

c1, c2 = st.columns(2)
c1.metric("Venituri", f"{venituri:,.0f} lei")
c2.metric("Cheltuieli", f"{cheltuieli:,.0f} lei")


for t in tranzactii:
    with st.container(border=True):
        c_info, c_suma, c_sterge = st.columns([5, 2, 1])

        with c_info:
            st.markdown(f"**{t['descriere']}**")
            st.caption(f"{t['data']} · {t['categorie']}")

        with c_suma:
            if t["tip"] == "venit":
                st.success(f"+{t['suma']:,.0f} lei", icon="⬆️")
            else:
                st.error(f"-{t['suma']:,.0f} lei", icon="⬇️")

        with c_sterge:
            if st.button("Sterge", key=f"sterge_{t['id']}"):
                ok, rezultat = api("DELETE", f"/tranzactii/{t['id']}")
                if ok:
                    st.rerun()
                else:
                    st.error(rezultat)
