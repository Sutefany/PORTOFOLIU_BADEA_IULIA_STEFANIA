import streamlit as st
from comun import api

st.title("📚 Ghiduri de cariera IT")

CATEGORII = ["Toate", "CV si portofoliu", "Interviu", "Negociere", "Roluri IT", "La job", "Altele"]

categorie = st.sidebar.selectbox("Categorie", CATEGORII)

params = {}
if categorie != "Toate":
    params["categorie"] = categorie

ok, ghiduri = api("GET", "/ghiduri", params=params)
if not ok:
    st.error(ghiduri)
    st.stop()

if not ghiduri:
    st.info("Niciun ghid pentru categoria aleasa. Adauga unul din 'Adauga ghid'.")
    st.stop()

st.caption(f"{len(ghiduri)} ghiduri")

for g in ghiduri:
    with st.container(border=True):
        c_info, c_sterge = st.columns([6, 1])

        with c_info:
            st.markdown(f"**{g['titlu']}**")
            st.caption(f"{g['categorie']} · adaugat pe {g['data']} · {len(g['continut'])} caractere")
            with st.expander("Continut"):
                st.markdown(g["continut"])

        with c_sterge:
            if st.button("Sterge", key=f"sterge_{g['id']}"):
                ok, rezultat = api("DELETE", f"/ghiduri/{g['id']}")
                if ok:
                    st.rerun()
                else:
                    st.error(rezultat)
