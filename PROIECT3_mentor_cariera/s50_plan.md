# Proiectul Mentor de carieră IT (plan de lucru)

## Ordinea de lucru

```
s50_model.py   ← baza de date (tabela Ghid + funcțiile CRUD)
     ↓
s50_schema.py  ← validarea datelor
     ↓
s50_rag.py     ← Chroma: add + query + delete
     ↓
s50_agent.py   ← mentorul AI
     ↓
s50_app.py     ← rutele HTTP
     ↓
s50_ui.py + comun.py   ← scheletul interfeței (gata scrise)
     ↓
s50_pages/*.py ← paginile
```

## Pasul 1 — `s50_model.py` (baza de date)

- [ ] **TODO 1.2** `Ghid` → tabela `s50_ghid`: `id`, `titlu` (**unique**),
  `categorie`, `continut` (**`Text`**), `data`; plus `__str__`
- [ ] **TODO 1.4a** `adauga_ghid(s, titlu, categorie, continut)`
- [ ] **TODO 1.4b** `toate_ghidurile(s, categorie=None)` → ordonate după titlu
- [ ] **TODO 1.4c** `gaseste_ghid_dupa_titlu(s, titlu)` → ghidul sau `None`
- [ ] **TODO 1.4d** `sterge_ghid(s, id)` → `True` / `False`

## Pasul 2 — `s50_schema.py` (validarea datelor)

- [ ] **TODO 2.1a** `Categorie(str, Enum)`: `CV si portofoliu`, `Interviu`, `Negociere`,
  `Roluri IT`, `La job`, `Altele`
- [ ] **TODO 2.1b** `GhidIn`: `titlu` 3–200 caractere, `categorie`, `continut` minim 50 caractere
- [ ] **TODO 2.2a–d** `MesajChat`, `ChatIn`, `ApelTool` (`tool` + `rezultat`), `ChatOut`

## Pasul 3 — `s50_rag.py` (Chroma)

- [ ] **TODO 3.1a** `indexeaza_ghid(ghid)` →
  `colectie.add(ids=[str(ghid.id)], documents=[ghid.continut], metadatas=[{"titlu": ghid.titlu}])`
- [ ] **TODO 3.1b** `indexeaza_toate(ghiduri)` → un `for` cu `indexeaza_ghid`
- [ ] **TODO 3.1c** `sterge_din_index(ghid_id)` → `colectie.delete(ids=[str(ghid_id)])`
- [ ] **TODO 3.2** `cauta(intrebare, n_rezultate=2)` → listă `{"titlu", "text", "distanta"}`

## Pasul 4 — `s50_agent.py` (mentorul AI)

- [ ] **TODO 4.1** tool-ul `cauta_in_ghiduri(intrebare)` → ghidurile găsite, fiecare cu
  titlul în față: `[Negocierea salariala]` + textul
- [ ] **TODO 4.2** `ruleaza_agent(mesaj, istoric)` → `(raspuns, apeluri)`

## Pasul 5 — `s50_app.py` (API-ul FastAPI)

- [ ] **TODO 5.1a** `GET /ghiduri?categorie=`
- [ ] **TODO 5.1b** `POST /ghiduri` (201) — titlu duplicat → `400`; apoi **`indexeaza_ghid`**
- [ ] **TODO 5.1c** `DELETE /ghiduri/{id}` — `404`; apoi **`sterge_din_index`**
- [ ] **TODO 5.2** `GET /cauta?intrebare=&n=2` — `n` în afara 1–5 → `400`
- [ ] **TODO 5.3** `POST /chat` — eroare de la OpenAI → `502`

## Pasul 6 — `comun.py` + `s50_ui.py`

`api(metoda, cale, ...)` întoarce `(ok, rezultat)`; `s50_ui.py` face meniul cu
cele 4 pagini. `API_URL` din `comun.py` trebuie să aibă **același port** ca
`uvicorn.run(...)` din `s50_app.py`.

## Pasul 7 — `s50_pages/` (paginile)

- [ ] **`ghiduri.py`** — TODO 1: filtrul de categorie; TODO 2: butonul Șterge
- [ ] **`adauga.py`** — TODO: `POST /ghiduri` cu `timeout=30`
- [ ] **`cautare.py`** — TODO: afișarea fiecărui ghid găsit (titlu, distanță, text)
- [ ] **`mentor.py`** — TODO 1: istoricul; TODO 2: salvarea mesajelor în `st.session_state`
