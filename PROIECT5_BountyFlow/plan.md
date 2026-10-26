## 1. Modelul — `get_db()` + `User` — `model.py`

- [ ] clasa `User` — username (unique) + parola_hash
- [ ] `creeaza_user`
- [ ] `gaseste_user_dupa_username`
- [ ] `get_db()` — dependency cu `yield`

## 2. Schema — cont și login — `schema.py`

- [ ] `UserIn`
- [ ] `LoginIn`
- [ ] `TokenOut`

## 3. Autentificare — `auth.py`

- [ ] `hash_parola` / `verifica_parola`
- [ ] `creeaza_token` / `decodeaza_token`
- [ ] `get_current_user` — dependency-ul "paznic"

## 4. FastAPI — `s40_app.py`

- [ ] `CORSMiddleware`
- [ ] `POST /register`
- [ ] `POST /login`
- [ ] `Depends(get_db)` + `Depends(get_current_user)` pe fiecare rută de task
- [ ] `GET /eu`
- [ ] test: fără token → 401; cu token valid → merge normal

## 5. Agentul — `agent.py`  

Deja rezolvate în fișier (se prezintă, nu se scriu):

- cele 5 tool-uri (schema JSON): `listeaza_task_uri`, `adauga_task`, `marcheaza_rezolvat`, `sterge_task`, `recompensa_disponibila`
- `ruleaza_agent(db, mesaj, istoric)` — bucla cu `MAX_PASI`, întoarce și tool-urile apelate

## 6. Streamlit — login obligatoriu — `ui.py`, `comun.py`, `pages/autentificare.py`

- [ ] `comun.py` — atașarea tokenului la fiecare cerere
- [ ] `comun.py` — tratarea unui 401 (sesiune expirată/invalidă)
- [ ] `ui.py` — gating-ul: doar pagina de login cât timp nu ești logat
- [ ] `pages/autentificare.py` — formularele de login + cont nou






