
import streamlit as st

# FORMULA = necesitati, dorinte, economii = venit_net * 0.50, venit_net * 0.30, venit_net * 0.20

c1, c2, c3 = st.columns(3)

with c2:
    st.title("🧠 Calculator de buget")
    st.caption("Introduceti venitul net pentru a calcula necesitatile, dorintele si economiile")

    with st.form("CALCUL BUGET:",clear_on_submit=True):
        venit_net = st.number_input("Salariul net", placeholder="Salariul net", step=1, value=5000)
        trimis = st.form_submit_button("Calculeaza", type="primary")

    if trimis:
        st.caption(f"FORMULA UTILIZATA: necesitati, dorinte, economii = venit_net * 0.50, venit_net * 0.30, venit_net * 0.20")
        necesitati, dorinte, economii = venit_net * 0.50, venit_net * 0.30, venit_net * 0.20
        st.balloons()
        st.info(f"Necesitati (50%): {necesitati}")
        st.info(f"Dorinte (30%): {dorinte}")
        st.info(f"Economii (20%): {economii}")

