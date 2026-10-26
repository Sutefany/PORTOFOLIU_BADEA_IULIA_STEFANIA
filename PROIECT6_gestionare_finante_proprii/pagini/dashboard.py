from datetime import date

import streamlit as st
from comun import api

st.title("📊 Dashboard")

luna = date.today().strftime("%Y-%m")
st.caption(f"Luna curenta: {luna}")

ok, sold = api("GET", "/sold", params={"luna": luna})
if not ok:
    st.error(sold)
    st.stop()

ok, cheltuieli = api("GET", "/tranzactii", params={"luna": luna, "tip": "cheltuiala"})
if not ok:
    st.error(cheltuieli)
    st.stop()

ok, abonamente = api("GET", "/abonamente")
if not ok:
    st.error(abonamente)
    st.stop()


with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Venituri", f"{sold['venituri']:,.0f} lei")
    c2.metric("Cheltuieli", f"{sold['cheltuieli']:,.0f} lei")
    c3.metric("Abonamente", f"{sold['abonamente']:,.0f} lei")
    c4.metric("Sold", f"{sold['sold']:,.0f} lei")

    procent = 0.0
    if sold["venituri"] > 0:
        cheltuit = sold["cheltuieli"] + sold["abonamente"]
        procent = cheltuit / sold["venituri"]
        if procent > 1:
            procent = 1.0

    st.progress(procent, text=f"Ai cheltuit {procent * 100:.0f}% din venituri luna asta")


c1, c2 = st.columns(2)

with c1:
    st.subheader("Cheltuieli pe categorie")
    pe_categorie = {}
    for t in cheltuieli:
        if t["categorie"] in pe_categorie:
            pe_categorie[t["categorie"]] = pe_categorie[t["categorie"]] + t["suma"]
        else:
            pe_categorie[t["categorie"]] = t["suma"]

    if pe_categorie:
        st.bar_chart(pe_categorie)
    else:
        st.info("Nicio cheltuiala luna asta.")

with c2:
    st.subheader("Abonamente active, pe categorie")
    pe_cat_ab = {}
    for a in abonamente:
        if a["activ"]:
            if a["categorie"] in pe_cat_ab:
                pe_cat_ab[a["categorie"]] = pe_cat_ab[a["categorie"]] + a["cost_lunar"]
            else:
                pe_cat_ab[a["categorie"]] = a["cost_lunar"]

    if pe_cat_ab:
        st.bar_chart(pe_cat_ab)
    else:
        st.info("Niciun abonament activ.")
