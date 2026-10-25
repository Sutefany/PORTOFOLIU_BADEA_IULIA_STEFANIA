# =============================================================
# PAGINA  -  Cautare (fara modelul de chat)
# =============================================================

import streamlit as st
from comun import api

st.title("🔎 Cautare in fise")
st.caption("Cautarea se face dupa SENS: incearca o intrebare care nu foloseste "
           "cuvintele din fise, ex: *ce trebuie sa scrie pe documentul prin care cer plata?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (fara modelul de chat)"):
    st.markdown(
        "Pe aceasta pagina **nu se foloseste modelul de chat**."
        "Scrie un subiect sau o întrebare pentru a găsi fisele relevante.\n\n"
        "- Rezultatele sunt afișate în ordinea relevanței.\n"
        "- Conținutul fiselor este afișat exact cum a fost salvat.\n"
        "- Poți deschide o fisa pentru a vedea toate detaliile.\n\n"
        "Dacă dorești un răspuns personalizat și explicații generate pe baza "
        "fiselor, folosește pagina **Profesor AI**."
    )

intrebare = st.text_input("Intrebare")
n = st.slider("Cate fise", min_value=1, max_value=5, value=2)

if intrebare:
    ok, rezultate = api("GET", "/cauta", params={"intrebare": intrebare, "n": n}, timeout=30)
    if not ok:
        st.error(rezultate)
        st.stop()

    for r in rezultate:
        with st.container(border=True):
            if r['distanta'] >= 0.7:
                st.write(f"{r['titlu']} :red[({r['distanta']})] - {r['text']}")
            else:
                st.write(f"{r['titlu']} :green[({r['distanta']})] - {r['text']}")

    st.caption("Distanta mai MICA = fisa mai potrivita. Chroma intoarce mereu "
               "n fise, chiar daca niciuna nu e relevanta - compara distantele.")
