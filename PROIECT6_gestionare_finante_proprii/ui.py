import streamlit as st

st.set_page_config(page_title="Bugetul meu", page_icon="💰", layout="wide")

pagina_tranzactii = st.Page("pagini/tranzactii.py", title="Tranzactii", icon="💸", default=True)
pagina_adauga = st.Page("pagini/adauga.py", title="Adauga tranzactie", icon="➕")
pagina_abonamente = st.Page("pagini/abonamente.py", title="Abonamente", icon="🔁")
pagina_dashboard = st.Page("pagini/dashboard.py", title="Dashboard", icon="📊")
pagina_consilier = st.Page("pagini/consilier.py", title="Consilier AI", icon="🤖")

navigare = st.navigation([pagina_tranzactii, pagina_adauga, pagina_abonamente,
                          pagina_dashboard, pagina_consilier])

navigare.run()
