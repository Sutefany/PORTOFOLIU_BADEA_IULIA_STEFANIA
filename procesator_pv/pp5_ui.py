
############################### PAGINILE DIN STREAMLIT + NAVIGARE ###############################

### IMPORTURI NECESARE

import streamlit as st

### CONFIGURAREA PAGINII PRINCIPALE- titlu, icon, layout

st.set_page_config(page_title="Procesator Procese Verbale", page_icon="📝", layout="wide")

### CONFIGURAREA PAGINILOR - pagina_ROL: listare, adaugare, modificare si stergere, asistent - localizare folder, titlu, icon

pagina_listare = st.Page("./pages/listare.py", title="Lista Proceselor Verbale", icon="📋", default=True)
pagina_adauga = st.Page("./pages/adauga.py", title="Adauga un proces verbal", icon="➕")
pagina_modifica_sterge = st.Page("./pages/modifica_sterge.py", title="Modifica/Sterge date", icon="📒")
pagina_asistent = st.Page("./pages/asistent.py", title="Asistent AI", icon="🤖")
pagina_descarca_excel = st.Page("./pages/descarca_excel.py", title="Descarca Situatia Generala de Lucrari", icon="🏗️")

### NAVIGARE PRIN PAGINI

navigare = st.navigation([pagina_listare, pagina_adauga, pagina_modifica_sterge, pagina_asistent, pagina_descarca_excel])

navigare.run()

