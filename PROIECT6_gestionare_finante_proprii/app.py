from fastapi import Depends, FastAPI, HTTPException

import model
from model import get_db, init_db
from schema import TranzactieIn, AbonamentIn, Tip, CategorieTranzactie, ChatIn, ChatOut
from agent import ruleaza_agent


init_db()

app = FastAPI(title="Bugetul meu", version="1.0.0 (app + consilier AI)")

# #############################################################
# PARTEA 1 - TRANZACTII  (plan: 3.1)
# #############################################################

@app.get("/tranzactii")
def lista_tranzactii(luna: str | None = None, tip: Tip | None = None,
                     categorie: CategorieTranzactie | None = None,
                     db=Depends(get_db)):
    tip_text = None
    if tip is not None:
        tip_text = tip.value

    categorie_text = None
    if categorie is not None:
        categorie_text = categorie.value

    try:
        rezultat = model.toate_tranzactiile(db, luna, tip_text, categorie_text)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"luna '{luna}' nu e in formatul YYYY-MM")

    lista = []
    for t in rezultat:
        lista.append({"id": t.id, "descriere": t.descriere, "tip": t.tip,
                      "categorie": t.categorie, "suma": t.suma, "data": t.data.isoformat()})
    return lista

@app.post("/tranzactii", status_code=201)
def adauga_tranzactie(data: TranzactieIn, db=Depends(get_db)):
    t = model.adauga_tranzactie(db, data.descriere, data.tip.value, data.categorie.value,
                                data.suma, data.data)
    return {"id": t.id, "descriere": t.descriere, "tip": t.tip,
            "categorie": t.categorie, "suma": t.suma, "data": t.data.isoformat()}


@app.delete("/tranzactii/{tranzactie_id}")
def sterge_tranzactie(tranzactie_id: int, db=Depends(get_db)):
    if not model.sterge_tranzactie(db, tranzactie_id):
        raise HTTPException(status_code=404, detail=f"tranzactia {tranzactie_id} nu exista")
    return {"sters": tranzactie_id}


# #############################################################
# PARTEA 2 - ABONAMENTE  (plan: 3.2)
# #############################################################

@app.get("/abonamente")
def lista_abonamente(db=Depends(get_db)):
    lista = []
    for a in model.toate_abonamentele(db):
        lista.append({"id": a.id, "nume": a.nume, "categorie": a.categorie,
                      "cost_lunar": a.cost_lunar, "zi_plata": a.zi_plata, "activ": a.activ})
    return lista

@app.post("/abonamente", status_code=201)
def adauga_abonament(data: AbonamentIn, db=Depends(get_db)):
    if model.gaseste_abonament_dupa_nume(db, data.nume) is not None:
        raise HTTPException(status_code=400, detail=f"abonamentul '{data.nume}' exista deja")
    a = model.adauga_abonament(db, data.nume, data.categorie.value, data.cost_lunar, data.zi_plata)
    return {"id": a.id, "nume": a.nume, "categorie": a.categorie,
            "cost_lunar": a.cost_lunar, "zi_plata": a.zi_plata, "activ": a.activ}

@app.put("/abonamente/{abonament_id}/comuta")
def comuta_abonament(abonament_id: int, db=Depends(get_db)):
    a = model.comuta_abonament(db, abonament_id)
    if a is None:
        raise HTTPException(status_code=404, detail=f"abonamentul {abonament_id} nu exista")
    return {"id": a.id, "nume": a.nume, "categorie": a.categorie,
            "cost_lunar": a.cost_lunar, "zi_plata": a.zi_plata, "activ": a.activ}

@app.delete("/abonamente/{abonament_id}")
def sterge_abonament(abonament_id: int, db=Depends(get_db)):
    if not model.sterge_abonament(db, abonament_id):
        raise HTTPException(status_code=404, detail=f"abonamentul {abonament_id} nu exista")
    return {"sters": abonament_id}


# #############################################################
# PARTEA 3 - SOLDUL  (plan: 3.3)
# #############################################################

@app.get("/sold")
def sold(luna: str | None = None, db=Depends(get_db)):
    if luna is None:
        luna = model.luna_curenta()
    try:
        return model.sold_luna(db, luna)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"luna '{luna}' nu e in formatul YYYY-MM")

# #############################################################
# PARTEA 4 - /chat: CONSILIERUL AI  (plan: 3.4 - dupa Pasul 4)
# #############################################################

@app.post("/chat", response_model=ChatOut)
def chat(data: ChatIn, db=Depends(get_db)):
    istoric = []
    for m in data.istoric:
        istoric.append(m.model_dump())

    try:
        raspuns, apeluri = ruleaza_agent(db, data.mesaj, istoric)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Eroare la modelul AI: {e}")
    return ChatOut(raspuns=raspuns, apeluri=apeluri)


import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000)
