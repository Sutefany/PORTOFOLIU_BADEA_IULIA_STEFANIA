import streamlit as st
from comun import api

st.title("🔁 Abonamente")

ok, abonamente = api("GET", "/abonamente")
if not ok:
    st.error(abonamente)
    st.stop()

nr_active = 0
total_lunar = 0
for a in abonamente:
    if a["activ"]:
        nr_active = nr_active + 1
        total_lunar = total_lunar + a["cost_lunar"]

c1, c2, c3 = st.columns(3)
c1.metric("Cost lunar", f"{total_lunar:,.0f} lei")
c2.metric("Cost anual", f"{total_lunar * 12:,.0f} lei")
c3.metric("Active", f"{nr_active} din {len(abonamente)}")


for a in abonamente:
    with st.container(border=True):
        c_info, c_stare, c_comuta, c_sterge = st.columns([4, 2, 1, 1])

        with c_info:
            st.markdown(f"**{a['nume']}** — {a['cost_lunar']:,.0f} lei/luna")
            st.caption(f"{a['categorie']} · se plateste pe {a['zi_plata']}")

        with c_stare:
            if a["activ"]:
                st.success("activ", icon="✅")
            else:
                st.warning("pe pauza", icon="⏸️")

        with c_comuta:
            if a["activ"]:
                eticheta = "Pauza"
            else:
                eticheta = "Activeaza"
            if st.button(eticheta, key=f"comuta_{a['id']}"):
                ok, rezultat = api("PUT", f"/abonamente/{a['id']}/comuta")
                if ok:
                    st.rerun()
                else:
                    st.error(rezultat)

        with c_sterge:
            if st.button("Sterge", key=f"sterge_{a['id']}"):
                ok, rezultat = api("DELETE", f"/abonamente/{a['id']}")
                if ok:
                    st.rerun()
                else:
                    st.error(rezultat)



st.subheader("Abonament nou")
with st.form("form_abonament_nou", clear_on_submit=True):
    nume = st.text_input("Nume", placeholder="ex: YouTube Premium")

    c1, c2, c3 = st.columns(3)
    categorie = c1.selectbox("Categorie", ["Streaming", "Muzica", "Sport", "Software",
                                           "Telefon & Internet", "Altele"])
    cost_lunar = c2.number_input("Cost lunar (lei)", min_value=0.0, step=5.0, value=30.0)
    zi_plata = c3.number_input("Zi de plata", min_value=1, max_value=31, value=1)

    trimis = st.form_submit_button("Adauga abonament", type="primary")

if trimis:
    ok, rezultat = api("POST", "/abonamente", json={
        "nume": nume, "categorie": categorie, "cost_lunar": cost_lunar, "zi_plata": zi_plata,
    })
    if ok:
        st.rerun()
    else:
        st.error(rezultat)
