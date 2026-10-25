# =============================================================
# PAGINA  -  Mentor AI
# =============================================================

import streamlit as st
from comun import api

st.title("🧭 Mentorul tau de cariera IT")
st.caption("Exemple: *Ce raspund la intrebarea despre cel mai mare defect?* · "
           "*Cum negociez salariul la prima oferta?* · "
           "*Am lucrat in contabilitate - ce rol din IT mi s-ar potrivi?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (RAG complet)"):
    st.markdown(
        "## Întreabă Profesorul AI\n\n"
        "Scrie o întrebare, iar Profesorul AI va consulta ghidurile disponibile "
        "și va formula un răspuns clar, pe baza informațiilor găsite.\n\n"
        "- Deschide secțiunea **📚 Surse** pentru a vedea ghidurile consultate.\n"
        "- Verifică informațiile importante direct în sursele afișate.\n"
        "- Pentru răspunsuri cât mai relevante, formulează întrebări clare și specifice.\n\n"
        "Dacă informația necesară nu se găsește în ghidurile disponibile, "
        "răspunsul poate fi incomplet sau inexact."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role", "content", "apeluri"}]

def arata_apeluri(apeluri):
    if apeluri:
        with st.expander("📚 Surse - ghidurile gasite"):
            for a in apeluri:
                st.caption(a["rezultat"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        arata_apeluri(m.get("apeluri"))

mesaj = st.chat_input("Intreaba-ma despre cariera in IT...")

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
