# Proiectul 3 — Antreprenor la început (plan de lucru)

## Ordinea de lucru

```
s50_model.py   ← baza de date (tabela Fisa + funcțiile CRUD)
     ↓
s50_schema.py  ← validarea datelor
     ↓
s50_rag.py     ← Chroma: add + query + delete
     ↓
s50_agent.py   ← asistentul AI
     ↓
s50_app.py     ← rutele HTTP
     ↓
s50_ui.py + comun.py   ← scheletul interfeței (gata scrise)
     ↓
s50_pages/*.py ← paginile
```

## Pasul 1 — `s50_model.py` (baza de date)

- [ ] **TODO 1.2** `Fisa` → tabela `s50_fisa`: `id`, `titlu` (**unique**),
  `categorie`, `continut` (**`Text`**), `data`; plus `__str__`
- [ ] **TODO 1.4a** `adauga_fisa(s, titlu, categorie, continut)`
- [ ] **TODO 1.4b** `toate_fisele(s, categorie=None)` → ordonate după titlu
- [ ] **TODO 1.4c** `gaseste_fisa_dupa_titlu(s, titlu)` → fișa sau `None`
- [ ] **TODO 1.4d** `sterge_fisa(s, id)` → `True` / `False`

## Pasul 2 — `s50_schema.py` (validarea datelor)

- [ ] **TODO 2.1a** `Categorie(str, Enum)`: `Forme juridice`, `Taxe`, `Facturare`,
  `Clienti si contracte`, `Freelancing`, `Altele`
- [ ] **TODO 2.1b** `FisaIn`: `titlu` 3–200 caractere, `categorie`, `continut` minim 50 caractere
- [ ] **TODO 2.2a–d** `MesajChat`, `ChatIn`, `ApelTool` (`tool` + `rezultat`), `ChatOut`

## Pasul 3 — `s50_rag.py` (Chroma)

**Gata scris:** colecția Chroma.

- [ ] **TODO 3.1a** `indexeaza_fisa(fisa)` →
  `colectie.add(ids=[str(fisa.id)], documents=[fisa.continut], metadatas=[{"titlu": fisa.titlu}])`
- [ ] **TODO 3.1b** `indexeaza_toate(fise)` → un `for` cu `indexeaza_fisa`
- [ ] **TODO 3.1c** `sterge_din_index(fisa_id)` → `colectie.delete(ids=[str(fisa_id)])`
- [ ] **TODO 3.2** `cauta(intrebare, n_rezultate=2)` → listă `{"titlu", "text", "distanta"}`

## Pasul 4 — `s50_agent.py` (asistentul AI)

- [ ] **TODO 4.1** tool-ul `cauta_in_fise(intrebare)` → fișele găsite, fiecare cu
  titlul în față: `[PFA sau SRL: ce forma juridica alegi]` + textul
- [ ] **TODO 4.2** `ruleaza_agent(mesaj, istoric)` → `(raspuns, apeluri)`

## Pasul 5 — `s50_app.py` (API-ul FastAPI)

- [ ] **TODO 5.1a** `GET /fise?categorie=`
- [ ] **TODO 5.1b** `POST /fise` (201) — titlu duplicat → `400`; apoi **`indexeaza_fisa`**
- [ ] **TODO 5.1c** `DELETE /fise/{id}` — `404`; apoi **`sterge_din_index`**
- [ ] **TODO 5.2** `GET /cauta?intrebare=&n=2` — `n` în afara 1–5 → `400`
- [ ] **TODO 5.3** `POST /chat` — eroare de la OpenAI → `502`

## Pasul 6 — `comun.py` + `s50_ui.py`

`api(metoda, cale, ...)` întoarce `(ok, rezultat)`; `s50_ui.py` face meniul cu
cele 4 pagini. `API_URL` din `comun.py` trebuie să aibă **același port** ca
`uvicorn.run(...)` din `s50_app.py`.

## Pasul 7 — `s50_pages/` (paginile)

- [ ] **`fise.py`** — TODO 1: filtrul de categorie; TODO 2: butonul Șterge
- [ ] **`adauga.py`** — TODO: `POST /fise` cu `timeout=30`
- [ ] **`cautare.py`** — TODO: afișarea fiecărei fișe găsite (titlu, distanță, text)
- [ ] **`asistent.py`** — TODO 1: istoricul; TODO 2: salvarea mesajelor în `st.session_state`