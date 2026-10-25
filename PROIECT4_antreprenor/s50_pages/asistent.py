# =============================================================
# PAGINA  -  Asistent AI
# =============================================================

import streamlit as st
from comun import api

st.title("🤖 Asistentul tau pentru afacerea proprie")
st.caption("Exemple: *Ce aleg la inceput: PFA sau SRL?* · "
           "*Cum calculez cat sa cer pe ora?* · *Ce trebuie sa contina contractul cu clientul?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (RAG complet)"):
    st.markdown(
         "## Întreabă Asistentul AI\n\n"
        "Scrie o întrebare, iar Asistentul AI va consulta fișele disponibile "
        "și va formula un răspuns clar, pe baza informațiilor găsite.\n\n"
        "- Deschide secțiunea **📚 Surse** pentru a vedea fișele consultate.\n"
        "- Verifică informațiile importante direct în sursele afișate.\n"
        "- Formulează întrebări clare și specifice pentru răspunsuri mai relevante.\n\n"
        "Dacă informația necesară nu se găsește în fișele disponibile, răspunsul "
        "poate fi incomplet sau inexact.\n\n"
        "Asistentul AI are rol informativ și educațional. Acesta nu înlocuiește "
        "serviciile unui contabil sau ale unui avocat."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role", "content", "apeluri"}]

def arata_apeluri(apeluri):
    if apeluri:
        with st.expander("📚 Surse - fisele gasite"):
            for a in apeluri:
                st.caption(a["rezultat"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        arata_apeluri(m.get("apeluri"))

mesaj = st.chat_input("Intreaba-ma despre PFA, SRL, taxe, clienti...")

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
