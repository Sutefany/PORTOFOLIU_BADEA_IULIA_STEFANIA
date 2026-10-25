# =============================================================
# PAGINA  -  Profesor AI  (ca Asistent AI de la s49)
# =============================================================

import streamlit as st
from comun import api

st.title("🎓 Profesorul tau de finante personale")
st.caption("Exemple: *Cheltuiesc 4000 de lei pe luna - cat ar trebui sa am deoparte?* · "
           "*Ce e DAE?* · *De ce sa platesc cardul de credit inainte sa investesc?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (RAG complet)"):
    st.markdown(
        "## Întreabă Profesorul AI\n\n"
        "Scrie o întrebare despre economie, finanțe sau noțiunile prezentate "
        "în lecții. Profesorul AI va găsi informațiile relevante și va formula "
        "un răspuns ușor de înțeles.\n\n"
        "- Consultă secțiunea **📚 Surse** pentru a vedea lecțiile folosite.\n"
        "- Compară răspunsul cu sursele atunci când ai nevoie de verificare.\n"
        "- Pentru rezultate mai bune, formulează întrebări clare și specifice.\n\n"
        "Profesorul AI are rol educațional și poate explica noțiuni generale, "
        "dar nu oferă recomandări personalizate despre produse sau decizii financiare."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role", "content", "apeluri"}]

def arata_apeluri(apeluri):
    if apeluri:
        with st.expander("📚 Surse - lectiile gasite"):
            for a in apeluri:
                st.caption(a["rezultat"])

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        arata_apeluri(m.get("apeluri"))

mesaj = st.chat_input("Intreaba-ma despre bani...")

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
