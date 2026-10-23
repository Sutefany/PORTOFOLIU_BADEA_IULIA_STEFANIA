
############################### PAGINA ASISTENT AI ###############################

# =============================================================
# PAGINA  -  Asistent AI  (nou in s44)
# =============================================================
# Chat-ul il stii de la 42.5: st.session_state.messages tine istoricul,
# st.chat_message il afiseaza, st.chat_input citeste mesajul nou.
#
# Pagina NU vorbeste direct cu OpenAI - trimite mesajul + istoricul la
# POST /chat (prin api() din comun.py), iar serverul
# ruleaza agentul. Sub fiecare raspuns aratam ce tool-uri a apelat.
# =============================================================

import streamlit as st
import pp5_comun

st.title("🤖 Asistent AI")
st.caption("Exemple: *Ce procese verbale exista?* · "
           "*Adauga o informatie* · "
           "*Sterge, modifica, filtreaza informatia*")

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role", "content", "apeluri"}]

# --- istoricul de pana acum ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# TODO: mesaj nou
#   - istoric = doar role + content (serverul nu vrea "apeluri")
#   - api("POST", "/chat", json={"mesaj": ..., "istoric": ...}, timeout=60)
#     (timeout mare: agentul poate face mai multe cereri la OpenAI)
#   - salveaza mesajul userului SI raspunsul in session_state

mesaj = st.chat_input("Scrie ceva...")   # None pana cand userul trimite ceva

if mesaj:
    with st.chat_message("user"):
        st.markdown(mesaj)

    istoric = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        with st.spinner("Ma gandesc..."):
            ok, rezultat = pp5_comun.api("POST", "/chat", json={"mesaj": mesaj, "istoric": istoric}, timeout=60)
        if not ok:
            st.error(rezultat)
            st.stop()
        st.markdown(rezultat["raspuns"])

    st.session_state.messages.append({"role": "user", "content": mesaj})
    st.session_state.messages.append({"role": "assistant", "content": rezultat["raspuns"],
                                      "apeluri": rezultat["apeluri"]})

if st.session_state.messages and st.sidebar.button("Conversatie noua"):
    st.session_state.messages = []
    st.rerun()

### AFISARE INSTRUCTIUNI IN SIDEBAR

with st.sidebar:

    with st.container(border= True):
        st.warning("INSTRUCTIUNI DE UTILIZARE")

        st.info("Utilizarea Asistentului AI - specializare: Procesator de date")
        st.caption("Intrebati Asistentul AI cu ce se ocupa si cum functioneaza")
        st.caption("Spuneti Asistentului AI ce doriti sa faceti. Variante:")
        st.caption("a. LISTAREA tuturor informatiilor (filtre posibile: echipa, cod, data, id)")
        st.caption("b. ADAUGAREA unui proces verbal (Informatii cerute: echipa, cod, valoare, data)")
        st.caption("c. MODIFICAREA unui proces verbal (Informatii cerute: echipa, cod, valoare, data)")
        st.caption("e. STERGEREA unui INTREG proces verbal (Informatii cerute: echipa, data)")
        st.caption("f. STERGEREA unui RAND dintr-un proces verbal (Informatii cerute: ID rand)")