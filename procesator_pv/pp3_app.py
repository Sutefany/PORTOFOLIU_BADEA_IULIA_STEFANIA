
############################### RUTELE HTTP ###############################

### IMPORTURI NECESARE

from fastapi import Depends, FastAPI, HTTPException

from proiect_personal_demo import pp1_model, pp2_schema
from pp1_model import get_db, init_db
from pp2_schema import  PvIn, Cod_Permis, ChatIn, ChatOut

from datetime import date

from pp4_agent import ruleaza_agent

init_db()
app = FastAPI(title="Procesator Procese Verbale", version="1.0.0 (proiect_personal + consilier AI)")

# ###################################################################################
# PARTEA 3A - PROCESE VERBALE
# ###################################################################################

# TODO 3a: GET /procese_verbale - lista proceselor verbale
#   Filtrele vin in URL, dupa ?, si sunt toate optionale:
#       GET http://127.0.0.1:8000/procese_verbale                                                   -> toate
#       GET http://127.0.0.1:8000/procese_verbale?echipa=Marius-arges&cod=COP6&data=2026-10-09      -> filtru dupa echipa, cod, zi

@app.get("/procese_verbale")
def lista_pv(echipa: str | None=None, cod: Cod_Permis | None=None, data: date | None=None, db=Depends(get_db)):
    lista = []

    if echipa is not None:
        try:
            echipa = pp2_schema.PvIn.norm_echipa(echipa)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    cod_verif = None
    if cod is not None:
        cod_verif = cod.value

    procese_verbale = pp1_model.toate_pv(db, echipa, cod_verif, data)

    for pv in procese_verbale:
        lista.append({
                "id": pv.id,
                "echipa": pv.echipa,
                "cod": pv.cod,
                "descriere": pv.descriere,
                "valori": pv.valori,
                "data": pv.data.isoformat()
        })
    return lista # va fi o lista goala daca nu gaseste nimic

# TODO 3b: POST /adauga_proces_verbal - adauga un proces verbal
#   Primeste in corpul cererii un JSON, pe care FastAPI il verifica singur cu PvIn inainte sa ruleze functia (date gresite -> 422):
#   {"echipa": "Radu- Arges", "cod": "COP1", "valori": 2.5, "data": date(2026, 9, 5)}
#   http://127.0.0.1:8000/adauga_procese_verbale

@app.post("/adauga_procese_verbale", status_code=201)
def adauga_proces_verbal(data: PvIn, db=Depends(get_db)):
    pv = pp1_model.adauga_pv(db, data.echipa, data.cod.value, data.valori, data.data)
    return {
        "id": pv.id,
        "echipa": pv.echipa,
        "cod": pv.cod,
        "descriere": pv.descriere,
        "valori": pv.valori,
        "data": pv.data.isoformat()
    }

# TODO 3c: DELETE /sterge_proces_verbal - sterge un proces verbal (TOATE VALORILE DIN ZIUA RESPECTIVA ALE ECHIPEI ALESE)
#   Folosita in: butonul "Sterge" din pagina Procese Verbale.
#   {echipa}/{data} din URL ajunge in parametrii pv_echipa si pv_data
#   ATENTIE: numele echipei trebuie normalizat -> pp2_schema -> PvIn -> norm_echipa
#   http://127.0.0.1:8000/sterge_proces_verbal/CALINA-%20CALARASI/2026-10-10

@app.delete("/sterge_proces_verbal/{pv_echipa}/{pv_data}")
def sterge_proces_verbal(pv_echipa: str, pv_data: date, db=Depends(get_db)):

    try:
        pv_echipa = pp2_schema.PvIn.norm_echipa(pv_echipa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    pv_sterse = pp1_model.sterge_pv(db, pv_echipa, pv_data)

    if not pv_sterse:
        raise HTTPException(status_code=404, detail="Procesul Verbal nu exista")

    return {"sterse": True,
            "echipa": pv_echipa,
            "data": pv_data.isoformat()}

# TODO 3d: DELETE /sterge_pv/id
#  va returna {"sters": id} - id-ul este unic si autoincrementat de baza de date
#   Folosita in: butonul "Sterge" din pagina Procese Verbale.
#   {id} din URL ajunge in parametriul id
#   http://127.0.0.1:8000/sterge_pv/13

@app.delete("/sterge_pv/{pv_id}")
def sterge_id(pv_id: int, db=Depends(get_db)):

    pv_sters = pp1_model.sterge_dupa_id(db, pv_id)

    if not pv_sters:
        raise HTTPException(status_code=404, detail="Procesul Verbal nu exista")

    return {"sters": pv_id}

# TODO 3e: PUT /modifica_proces_verbal - actualizare dupa id => VALOARE, COD, DATA si/sau ECHIPA
#   Folosita in: butonul Modifica_pv din pagina Modifica_PV
#   http://127.0.0.1:8000/modifica_proces_verbal/8?echipa_noua=mARIUS-%20cLUJ&cod_nou=COP16&data_noua=2026-10-09&valoare_noua=22

@app.put("/modifica_proces_verbal/{pv_id}")
def modifica_proces_verbal(pv_id: int, update: PvIn, db=Depends(get_db)):

    pv_cautat = pp1_model.modificare_pv(db, pv_id, update.echipa, update.cod, update.data, update.valori)

    if pv_cautat is None:
        raise HTTPException(404, f"Procesul verbal nr. {pv_id} nu exista")

    return {
        "id": pv_cautat.id,
        "echipa": pv_cautat.echipa,
        "descriere": pv_cautat.descriere,
        "cod": pv_cautat.cod,
        "valori": pv_cautat.valori,
        "data": pv_cautat.data.isoformat()
    }

# ###################################################################################
# PARTEA 3B - TOTAL_KM/ ZI, ECHIPA si TOTAL_DUPA_COD
# ###################################################################################

# TODO 3f: GET/total_km/echipa/data - nr. total de kilometri intr-o zi a unei echipe
#  Folosita in: ...
#  GET/total_km/Radu-Arges/2026-10-09
#  http://127.0.0.1:8000/total_km/echipa/data?echipa=MARIUS-ARGES&data=2026-10-09

@app.get("/total_km/echipa/data")
def total_km_echipa_zi(echipa: str, data: date, db=Depends(get_db)):
    try:
        echipa = pp2_schema.PvIn.norm_echipa(echipa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    total_km = pp1_model.total_km(db, echipa, data)

    return total_km

# TODO 3g: GET/total_cod/echipa/cod/data - nr. total de kilometri intr-o zi a unei echipe
#  http://127.0.0.1:8000/total_cod/echipa/cod/data?echipa=MARIUS-ARGES&cod=COP6&data=2026-10-09

@app.get("/total_cod/echipa/cod/data")
def total_cod(echipa: str, cod: Cod_Permis, data: date, db=Depends(get_db)):
    try:
        echipa = pp2_schema.PvIn.norm_echipa(echipa)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    total_zi = pp1_model.total_dupa_cod(db, echipa, cod, data)

    return total_zi

# ###################################################################################
# PARTEA 3C - chat: CONSILIERUL AI
# ###################################################################################

# TODO 3h: POST /chat - trimite mesajul utilizatorului la agent
#   Folosita in: pagina Consilier AI. Pagina nu vorbeste direct cu
#   OpenAI, ci prin aceasta ruta.
#   Primeste un JSON verificat cu ChatIn:
#       {"mesaj": "Am dat 45 lei pe pizza", "istoric": [{"role": "user", "content": "..."}, ...]}
#
#   Pasi:
#   1. data.istoric e o lista de obiecte MesajChat, dar agentul vrea o
#      lista de DICTIONARE. Construiesti lista istoric cu un for: pentru
#      fiecare mesaj m adaugi m.model_dump()  -> {"role": ..., "content": ...}
#   2. Chemi agentul: raspuns, apeluri = ruleaza_agent(db, data.mesaj, istoric)
#      Pune apelul in try: orice eroare (cheie OpenAI gresita, fara internet)
#      -> raise HTTPException(502, f"Eroare la modelul AI: {e}")
#      (502 = a cazut un serviciu extern, nu e vina cererii)
#   3. return ChatOut(raspuns=raspuns, apeluri=apeluri)

@app.post("/chat", response_model=ChatOut)
def chat(data: ChatIn, db=Depends(get_db)):
    istoric = [m.model_dump() for m in data.istoric]
    try:
        raspuns, apeluri = ruleaza_agent(db, data.mesaj, istoric)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Eroare la modelul AI: {e}")
    return ChatOut(raspuns=raspuns, apeluri=apeluri)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


















