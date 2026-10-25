from fastapi import Depends, FastAPI, HTTPException

import s50_model
import s50_rag
from s50_model import get_db, init_db
from s50_schema import Categorie, LectieIn, ChatIn, ChatOut
from s50_agent import ruleaza_agent

init_db()
with s50_model.SessionLocal() as s:
    s50_rag.indexeaza_toate(s50_model.toate_lectiile(s))

app = FastAPI(title="Educatie financiara personala", version="1.0.0 (s50, RAG)")

def lectie_dict(l):
    return {"id": l.id, "titlu": l.titlu, "categorie": l.categorie,
            "continut": l.continut, "data": l.data.isoformat()}

# #############################################################
# PARTEA 1 - LECTII  (plan: 5.1)
# #############################################################

@app.get("/lectii")
def lista_lectii(categorie: Categorie | None = None, db=Depends(get_db)):
    categorie_text = None
    if categorie is not None:
        categorie_text = categorie.value
    return [lectie_dict(l) for l in s50_model.toate_lectiile(db, categorie_text)]

@app.post("/lectii", status_code=201)
def adauga_lectie(data: LectieIn, db=Depends(get_db)):
    l = s50_model.gaseste_lectie_dupa_titlu(db, data.titlu)
    if l:
        raise HTTPException(400, f"lectia '{data.titlu}' exista deja")
    l = s50_model.adauga_lectie(db, data.titlu, data.categorie.value, data.continut)
    s50_rag.indexeaza_lectie(l)
    return lectie_dict(l)

@app.delete("/lectii/{lectie_id}")
def sterge_lectie(lectie_id: int, db=Depends(get_db)):
    l = s50_model.sterge_lectie(db, lectie_id)
    if not l:
        raise HTTPException(404, f"lectia cu id-ul '{lectie_id}' nu exista")
    s50_rag.sterge_din_index(lectie_id)
    return {"sters": lectie_id}

# #############################################################
# PARTEA 2 - CAUTARE  (plan: 5.2)
# #############################################################

@app.get("/cauta")
def cauta(intrebare: str, n: int = 2):
    if n < 1 or n > 5:
        raise HTTPException(400, f"n trebuie sa fie intre 1 si 5")
    return s50_rag.cauta(intrebare, n)

# #############################################################
# PARTEA 3 - /chat: PROFESORUL  (plan: 5.3 - dupa Pasul 4)
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