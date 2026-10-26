import streamlit as st
from comun import api

st.title("🔐 Bounty Board")

tab_login, tab_cont_nou = st.tabs(["Login", "Cont nou"])

with tab_login:
    with st.form("form_login"):
        username = st.text_input("Username", key="login_username")
        parola = st.text_input("Parola", type="password", key="login_parola")
        trimis = st.form_submit_button("Login", type="primary")

    if trimis:
        ok, rezultat = api("POST", "/login", cu_token=False,
                            json={"username": username, "parola": parola})
        if ok:
            st.session_state.token = rezultat["access_token"]
            st.session_state.username = username
            st.rerun()
        else:
            st.error(rezultat)

with tab_cont_nou:
    with st.form("form_cont_nou"):
        username_nou = st.text_input("Username", key="reg_username")
        parola_noua = st.text_input("Parola (minim 6 caractere)", type="password", key="reg_parola")
        trimis_cont = st.form_submit_button("Creeaza cont")

    if trimis_cont:
        ok, rezultat = api("POST", "/register", cu_token=False,
                            json={"username": username_nou, "parola": parola_noua})
        if ok:
            st.success("Cont creat! Acum te poti loga din tab-ul Login.")
        else:
            st.error(rezultat)
