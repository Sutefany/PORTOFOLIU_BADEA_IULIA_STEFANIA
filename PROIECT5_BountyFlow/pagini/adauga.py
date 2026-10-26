import streamlit as st
from comun import api

st.title("➕ Adauga task")

with st.form("form_task_nou", clear_on_submit=True):
    titlu = st.text_input("Titlu", placeholder="ex: Fix bug la login")

    c1, c2 = st.columns(2)
    limbaj = c1.selectbox("Limbaj", ["Python", "JavaScript", "Go", "Rust"])
    dificultate = c2.selectbox("Dificultate", ["usor", "mediu", "greu"])

    recompensa = st.number_input("Recompensa (RON)", min_value=0.0, step=10.0, value=50.0)

    trimis = st.form_submit_button("Creeaza task", type="primary")

if trimis:
    ok, rezultat = api("POST", "/task-uri", json={
        "titlu": titlu,
        "limbaj": limbaj,
        "dificultate": dificultate,
        "recompensa": recompensa,
    })
    if ok:
        st.success(f"Task creat: \"{rezultat['titlu']}\" (id {rezultat['id']})")
        st.balloons()
    else:
        st.error(rezultat)
