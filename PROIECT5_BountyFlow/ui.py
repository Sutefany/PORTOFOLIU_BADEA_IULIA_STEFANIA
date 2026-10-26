import streamlit as st

st.set_page_config(page_title="Bounty Board", page_icon="🧩", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

pagina_login = st.Page("pagini/autentificare.py", title="Login", icon="🔐", default=True)

if st.session_state.token is None:
    navigare = st.navigation([pagina_login])

else:
    pagina_lista = st.Page("./pagini/lista.py", title="Task-uri", icon="📋", default=True)
    pagina_adauga = st.Page("./pagini/adauga.py", title="Adauga task", icon="➕")
    pagina_dashboard = st.Page("./pagini/dashboard.py", title="Dashboard", icon="📊")
    pagina_asistent = st.Page("./pagini/asistent.py", title="Asistent AI", icon="🤖")

    with st.sidebar:
        st.caption(f"Logat ca **{st.session_state.username}**")
        if st.button("Logout", width="stretch"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()

    navigare = st.navigation([pagina_lista, pagina_adauga, pagina_dashboard, pagina_asistent])

navigare.run()
