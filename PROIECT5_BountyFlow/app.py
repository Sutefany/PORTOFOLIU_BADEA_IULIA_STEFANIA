from fastapi import Depends, FastAPI, HTTPException

import model
from model import get_db, init_db
from agent import ruleaza_agent
from schema import TaskIn, UserIn, LoginIn, TokenOut, ChatIn, ChatOut
from auth import hash_parola, verifica_parola, creeaza_token, get_current_user

init_db()

app = FastAPI(title="Bounty Board", version="0.7.0 (s44, + asistent AI, fara autentificare)")

# #############################################################
# PARTEA 1 - CONT: /register si /login
# #############################################################

@app.post("/register", status_code=201)
def register(data: UserIn, db=Depends(get_db)):
    if model.gaseste_user_dupa_username(db, data.username) is not None:
        raise HTTPException(status_code=400, detail="username-ul e deja folosit")
    hash_ = hash_parola(data.parola)
    model.creeaza_user(db, data.username, hash_)
    return {"username": data.username}

@app.post("/login", response_model=TokenOut)
def login(data: LoginIn, db=Depends(get_db)):
    user = model.gaseste_user_dupa_username(db, data.username)
    if user is None or not verifica_parola(data.parola, user.parola_hash):
        raise HTTPException(status_code=401, detail="username sau parola gresite")
    token = creeaza_token(user.username)
    return TokenOut(access_token=token)

# #############################################################
# PARTEA 1 - RUTELE de task-uri
# #############################################################

@app.get("/task-uri")
def lista_task_uri(db=Depends(get_db), user=Depends(get_current_user)):
    return [{"id": t.id, "titlu": t.titlu, "limbaj": t.limbaj,
             "dificultate": t.dificultate, "recompensa": t.recompensa,
             "rezolvat": t.rezolvat} for t in model.toate_task_urile(db)]

@app.get("/task-uri/{task_id}")
def un_task(task_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    t = model.un_task(db, task_id)
    if t is None:
        raise HTTPException(status_code=404, detail=f"task-ul {task_id} nu exista")
    return {"id": t.id, "titlu": t.titlu, "limbaj": t.limbaj,
            "dificultate": t.dificultate, "recompensa": t.recompensa,
            "rezolvat": t.rezolvat}

@app.post("/task-uri", status_code=201)
def adauga_task(data: TaskIn, db=Depends(get_db), user=Depends(get_current_user)):
    t = model.adauga_task(db, data.titlu, data.limbaj, data.dificultate, data.recompensa)
    return {"id": t.id, "titlu": t.titlu, "limbaj": t.limbaj,
            "dificultate": t.dificultate, "recompensa": t.recompensa,
            "rezolvat": t.rezolvat}

@app.put("/task-uri/{task_id}/rezolva")
def rezolva_task(task_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    t = model.marcheaza_rezolvat(db, task_id)
    if t is None:
        raise HTTPException(status_code=404, detail=f"task-ul {task_id} nu exista")
    return {"id": t.id, "rezolvat": t.rezolvat}

@app.delete("/task-uri/{task_id}")
def sterge_task(task_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    gasit = model.sterge_task(db, task_id)
    if not gasit:
        raise HTTPException(status_code=404, detail=f"task-ul {task_id} nu exista")
    return {"sters": task_id}

@app.get("/recompensa-disponibila")
def recompensa_disponibila(db=Depends(get_db), user=Depends(get_current_user)):
    return {"recompensa_totala": model.recompensa_disponibila(db)}


# #############################################################
# PARTEA 2 - /chat: ASISTENTUL AI
# #############################################################

@app.post("/chat", response_model=ChatOut)
def chat(data: ChatIn, db=Depends(get_db), user=Depends(get_current_user)):
    istoric = [m.model_dump() for m in data.istoric]
    try:
        raspuns, apeluri = ruleaza_agent(db, data.mesaj, istoric)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Eroare la modelul AI: {e}")
    return ChatOut(raspuns=raspuns, apeluri=apeluri)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
