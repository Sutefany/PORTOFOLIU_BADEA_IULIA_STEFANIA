import streamlit as st
from comun import api

st.title("📊 Dashboard")

ok, task_uri = api("GET", "/task-uri")
if not ok:
    st.error(task_uri)
    st.stop()

ok, recompensa = api("GET", "/recompensa-disponibila")
if not ok:
    st.error(recompensa)
    st.stop()

if not task_uri:
    st.info("Nu exista task-uri inca pentru statistici.")
    st.stop()

nr_total = len(task_uri)
nr_rezolvate = sum(1 for t in task_uri if t["rezolvat"])
nr_deschise = nr_total - nr_rezolvate
procent_rezolvate = nr_rezolvate / nr_total * 100

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Task-uri", nr_total)
    c2.metric("Rezolvate", nr_rezolvate)
    c3.metric("Deschise", nr_deschise)
    c4.metric("Recompensa disponibila", f"{recompensa['recompensa_totala']:.0f} RON")

    st.progress(
        procent_rezolvate / 100,
        text=f"{procent_rezolvate:.0f}% din task-uri rezolvate ({nr_rezolvate}/{nr_total})",
    )

st.subheader("Task-uri pe categorii")
c1, c2 = st.columns(2)

with c1:
    st.caption("Dupa limbaj")
    pe_limbaj = {}
    for t in task_uri:
        pe_limbaj[t["limbaj"]] = pe_limbaj.get(t["limbaj"], 0) + 1
    pe_limbaj = dict(sorted(pe_limbaj.items(), key=lambda pereche: pereche[1], reverse=True))
    st.bar_chart(pe_limbaj)

with c2:
    st.caption("Dupa dificultate")
    pe_dificultate = {}
    for t in task_uri:
        pe_dificultate[t["dificultate"]] = pe_dificultate.get(t["dificultate"], 0) + 1
    pe_dificultate = dict(sorted(pe_dificultate.items(), key=lambda pereche: pereche[1], reverse=True))
    st.bar_chart(pe_dificultate)

st.subheader("Cele mai valoroase task-uri deschise")
deschise = [t for t in task_uri if not t["rezolvat"]]
top_deschise = sorted(deschise, key=lambda t: t["recompensa"], reverse=True)[:5]

if top_deschise:
    st.dataframe(
        [{"Titlu": t["titlu"], "Limbaj": t["limbaj"],
          "Dificultate": t["dificultate"], "Recompensa (RON)": t["recompensa"]}
         for t in top_deschise],
        hide_index=True,
        width="stretch",
    )
else:
    st.success("Toate task-urile sunt rezolvate!")
