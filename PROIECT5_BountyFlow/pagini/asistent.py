# =============================================================
# PAGINA  -  Asistent AI  (nou in s44)
# =============================================================

import streamlit as st
from comun import api

st.title("🤖 Asistent AI")
st.caption("Exemple: *Ce task-uri de Python sunt nerezolvate?* · "
           "*Adauga un task: Scrie teste, Python, mediu, 120 lei* · "
           "*Am terminat dark mode-ul, marcheaza-l rezolvat*")

if "messages" not in st.session_state:
    st.session_state.messages = []

def arata_apeluri(apeluri):
    if apeluri:
        with st.expander(f"🔧 {len(apeluri)} tool-uri apelate"):
            for a in apeluri:
                st.markdown(f"**{a['tool']}** `{a['argumente']}`")
                st.caption(a["rezultat"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        arata_apeluri(m.get("apeluri"))

mesaj = st.chat_input("Scrie ceva...")

if mesaj:
    with st.chat_message("user"):
        st.markdown(mesaj)

    istoric = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        with st.spinner("Ma gandesc..."):
            ok, rezultat = api("POST", "/chat", json={"mesaj": mesaj, "istoric": istoric}, timeout=60)
        if not ok:
            st.error(rezultat)
            st.stop()
        st.markdown(rezultat["raspuns"])
        arata_apeluri(rezultat["apeluri"])

    st.session_state.messages.append({"role": "user", "content": mesaj})
    st.session_state.messages.append({"role": "assistant", "content": rezultat["raspuns"],
                                      "apeluri": rezultat["apeluri"]})

if st.session_state.messages and st.sidebar.button("Conversatie noua"):
    st.session_state.messages = []
    st.rerun()
