from fastapi import Depends, FastAPI, HTTPException

import s50_model
import s50_rag
from s50_model import get_db, init_db
from s50_schema import Categorie, GhidIn, ChatIn, ChatOut
from s50_agent import ruleaza_agent

init_db()
with s50_model.SessionLocal() as s:
    s50_rag.indexeaza_toate(s50_model.toate_ghidurile(s))

app = FastAPI(title="Mentor de cariera IT", version="1.0.0 (s50, RAG)")

def ghid_dict(g):
    return {"id": g.id, "titlu": g.titlu, "categorie": g.categorie,
            "continut": g.continut, "data": g.data.isoformat()}

# #############################################################
# PARTEA 1 - GHIDURI  (plan: 5.1)
# #############################################################

@app.get("/ghiduri")
def lista_ghiduri(categorie: Categorie | None = None, db=Depends(get_db)):
    categorie_text = None
    if categorie is not None:
        categorie_text = categorie.value
    return [ghid_dict(g) for g in s50_model.toate_ghidurile(db, categorie_text)]

@app.post("/ghiduri", status_code=201)
def adauga_ghid(data: GhidIn, db=Depends(get_db)):
    g = s50_model.gaseste_ghid_dupa_titlu(db, data.titlu)
    if g:
        raise HTTPException(400, f"ghidul '{data.titlu}' exista deja")
    g = s50_model.adauga_ghid(db, data.titlu, data.categorie.value, data.continut)
    s50_rag.indexeaza_ghid(g)
    return ghid_dict(g)

@app.delete("/ghiduri/{ghid_id}")
def sterge_ghid(ghid_id: int, db=Depends(get_db)):
    g = s50_model.sterge_ghid(db, ghid_id)
    if not g:
        raise HTTPException(404, f"ghidul cu id-ul '{ghid_id}' nu exista")
    s50_rag.sterge_din_index(ghid_id)
    return {"sters": ghid_id}

# #############################################################
# PARTEA 2 - CAUTARE  (plan: 5.2)
# #############################################################

@app.get("/cauta")
def cauta(intrebare: str, n: int = 2):
    if n < 1 or n > 5:
        raise HTTPException(400, f"n trebuie sa fie intre 1 si 5")
    return s50_rag.cauta(intrebare, n)

# #############################################################
# PARTEA 3 - /chat: MENTORUL  (plan: 5.3 - dupa Pasul 4)
# #############################################################

@app.post("/chat", response_model=ChatOut)
def chat(data: ChatIn):
    istoric = []
    for m in data.istoric:
        istoric.append(m.model_dump())
    try:
        raspuns, apeluri = ruleaza_agent(data.mesaj, istoric)
    except Exception as e:
        HTTPException(502, f"Eroare la modelul AI: {e}")
    return ChatOut(raspuns=raspuns, apeluri=apeluri)

import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8005)