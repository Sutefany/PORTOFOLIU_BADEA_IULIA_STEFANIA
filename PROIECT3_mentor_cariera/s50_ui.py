import streamlit as st

st.set_page_config(page_title="Mentor de cariera IT", page_icon="🧭", layout="wide")

pagina_ghiduri = st.Page("s50_pages/ghiduri.py", title="Ghiduri", icon="📚", default=True)
pagina_adauga = st.Page("s50_pages/adauga.py", title="Adauga ghid", icon="➕")
pagina_cautare = st.Page("s50_pages/cautare.py", title="Cautare", icon="🔎")
pagina_mentor = st.Page("s50_pages/mentor.py", title="Mentor AI", icon="🧭")

navigare = st.navigation([pagina_ghiduri, pagina_adauga, pagina_cautare, pagina_mentor])

navigare.run()
