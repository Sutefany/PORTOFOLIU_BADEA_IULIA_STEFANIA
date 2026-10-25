# Proiectul Educație financiară personală (plan de lucru)

## Ordinea de lucru

```
s50_model.py   ← baza de date (tabela Lectie + funcțiile CRUD)
     ↓
s50_schema.py  ← validarea datelor
     ↓
s50_rag.py     ← Chroma: add + query + delete
     ↓
s50_agent.py   ← profesorul AI
     ↓
s50_app.py     ← rutele HTTP
     ↓
s50_ui.py + comun.py   ← scheletul interfeței (gata scrise)
     ↓
s50_pages/*.py ← paginile
```

## Pasul 1 — `s50_model.py` (baza de date)

- [ ] **TODO 1.2** `Lectie` → tabela `s50_lectie`: `id`, `titlu` (**unique**),
  `categorie`, `continut` (**`Text`**), `data`; plus `__str__`
- [ ] **TODO 1.4a** `adauga_lectie(s, titlu, categorie, continut)`
- [ ] **TODO 1.4b** `toate_lectiile(s, categorie=None)` → ordonate după titlu
- [ ] **TODO 1.4c** `gaseste_lectie_dupa_titlu(s, titlu)` → lecția sau `None`
- [ ] **TODO 1.4d** `sterge_lectie(s, id)` → `True` / `False`

## Pasul 2 — `s50_schema.py` (validarea datelor)

- [ ] **TODO 2.1a** `Categorie(str, Enum)`: `Buget`, `Economii`, `Credite`,
  `Investitii`, `Pensie`, `Altele`
- [ ] **TODO 2.1b** `LectieIn`: `titlu` 3–200 caractere, `categorie`, `continut` minim 50 caractere
- [ ] **TODO 2.2a–d** `MesajChat`, `ChatIn`, `ApelTool` (`tool` + `rezultat`), `ChatOut`

## Pasul 3 — `s50_rag.py` (Chroma)

- [ ] **TODO 3.1a** `indexeaza_lectie(lectie)` →
  `colectie.add(ids=[str(lectie.id)], documents=[lectie.continut], metadatas=[{"titlu": lectie.titlu}])`
- [ ] **TODO 3.1b** `indexeaza_toate(lectii)` → un `for` cu `indexeaza_lectie`
- [ ] **TODO 3.1c** `sterge_din_index(lectie_id)` → `colectie.delete(ids=[str(lectie_id)])`
- [ ] **TODO 3.2** `cauta(intrebare, n_rezultate=2)` → listă `{"titlu", "text", "distanta"}`

## Pasul 4 — `s50_agent.py` (profesorul AI)

- [ ] **TODO 4.1** tool-ul `cauta_in_lectii(intrebare)` → lecțiile găsite, fiecare cu
  titlul în față: `[Fondul de urgenta]` + textul
- [ ] **TODO 4.2** `ruleaza_agent(mesaj, istoric)` → `(raspuns, apeluri)`

## Pasul 5 — `s50_app.py` (API-ul FastAPI)

- [ ] **TODO 5.1a** `GET /lectii?categorie=`
- [ ] **TODO 5.1b** `POST /lectii` (201) — titlu duplicat → `400`; apoi **`indexeaza_lectie`**
- [ ] **TODO 5.1c** `DELETE /lectii/{id}` — `404`; apoi **`sterge_din_index`**
- [ ] **TODO 5.2** `GET /cauta?intrebare=&n=2` — `n` în afara 1–5 → `400`
- [ ] **TODO 5.3** `POST /chat` — eroare de la OpenAI → `502`

## Pasul 6 — `comun.py` + `s50_ui.py` (gata scrise)

`api(metoda, cale, ...)` întoarce `(ok, rezultat)`; `s50_ui.py` face meniul cu
cele 4 pagini. `API_URL` din `comun.py` trebuie să aibă **același port** ca
`uvicorn.run(...)` din `s50_app.py`.

## Pasul 7 — `s50_pages/` (paginile)

- [ ] **`lectii.py`** — TODO 1: filtrul de categorie; TODO 2: butonul Șterge
- [ ] **`adauga.py`** — TODO: `POST /lectii` cu `timeout=30`
- [ ] **`cautare.py`** — TODO: afișarea fiecărei lecții găsite (titlu, distanță, text)
- [ ] **`profesor.py`** — TODO 1: istoricul; TODO 2: salvarea mesajelor în `st.session_state`
