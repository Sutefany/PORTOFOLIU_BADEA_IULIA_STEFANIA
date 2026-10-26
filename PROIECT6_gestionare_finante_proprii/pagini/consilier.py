# =============================================================
# PAGINA  -  Consilier AI  (ca la s44)
# =============================================================

import streamlit as st
from comun import api

st.title("🤖 Consilier AI")
st.caption("Exemple: *Am dat 45 lei pe pizza azi* · "
           "*Cat am cheltuit pe mancare luna asta?* · "
           "*M-am abonat la YouTube Premium, 26 lei, pe 8* · "
           "*Cat imi ramane luna asta? Pe ce abonamente as putea taia?*")

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

    istoric = []
    for m in st.session_state.messages:
        istoric.append({"role": m["role"], "content": m["content"]})

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
