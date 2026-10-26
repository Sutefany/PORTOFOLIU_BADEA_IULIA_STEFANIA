
## Ordinea de lucru

```
model.py   ← baza de date (tabele + funcții care citesc/scriu)
     ↓
schema.py  ← ce date sunt acceptate de la client (validare)
     ↓
app.py     ← rutele HTTP (folosesc model + schema)
     ↓
agent.py   ← consilierul AI (folosește model + schema)
     ↓
ui.py + comun.py   ← scheletul interfeței Streamlit (gata scrise)
     ↓
pages/*.py ← paginile (vorbesc cu API-ul prin comun.api)
```

---

## Pasul 1 — `model.py` (baza de date)

**Scop:** tabelele din MySQL și funcțiile care le citesc și le modifică.
Restul aplicației nu scrie niciodată SQL direct — apelează funcțiile de aici.

- conexiunea: (`engine`, `SessionLocal`, `Base`, `adauga_date_initiale`, `init_db`,
`luna_curenta`, `get_db`).

### 1.2 Modelele (tabelele)
- [ ] **TODO 1.2a** `Tranzactie` → tabela `tranzactie`: `id`, `descriere`,
  `tip` (`"venit"` / `"cheltuiala"`), `categorie`, `suma`, `data`
- [ ] **TODO 1.2b** `Abonament` → tabela `abonament`: `id`, `nume` (**unique**),
  `categorie`, `cost_lunar`, `zi_plata`, `activ` (implicit `True`)
- câte un `__str__`, ca `print(obiect)` să afișeze un rând clar:
  `Tranzactie #4: cheltuiala 380.0 lei - Cumparaturi Mega (mancare, 2026-10-03)`
  `Abonament #1: Netflix - 55.0 lei/luna, plata pe 5 (activ)`

### 1.3 Pornirea bazei de date
- [ ] **TODO 1.3a** `reset_db()`

### 1.4 CRUD Tranzacție
- [ ] **TODO 1.4a** `interval_luna("2026-09")` → `(date(2026, 9, 1), date(2026, 10, 1))`
  - atenție la decembrie: luna următoare este ianuarie din anul următor
  - fără `try`/`except` și fără `raise`: la un text greșit Python aruncă
    singur `ValueError`, iar `app.py` o transformă în 400
- [ ] **TODO 1.4c** `adauga_tranzactie(s, ...)` → întoarce tranzacția salvată
- [ ] **TODO 1.4d** `toate_tranzactiile(s, luna=None, tip=None, categorie=None)`
  - interogarea se construiește pas cu pas: `query = query.where(...)`
    **doar** pentru filtrele date; ordonate de la cea mai nouă
- [ ] **TODO 1.4e** `sterge_tranzactie(s, id)` → `True` / `False`

### 1.5 CRUD Abonament
- [ ] **TODO 1.5a** `adauga_abonament(s, nume, categorie, cost_lunar, zi_plata)`
- [ ] **TODO 1.5b** `gaseste_abonament_dupa_nume(s, nume)` → abonamentul sau `None`
- [ ] **TODO 1.5c** `toate_abonamentele(s)` → de la cel mai scump
- [ ] **TODO 1.5d** `comuta_abonament(s, id)` → `activ = not activ`; `None` dacă nu există
- [ ] **TODO 1.5e** `sterge_abonament(s, id)` → `True` / `False`

### 1.6 Soldul lunii
- [ ] **TODO 1.6** `sold_luna(s, luna)` →
  `{"luna", "venituri", "cheltuieli", "abonamente", "sold"}`
  - `sold = venituri - cheltuieli - abonamente ACTIVE` (abonamentele intră în fiecare lună)

## Pasul 2 — `schema.py` (validarea datelor)

### 2.1 Tranzacție
- [ ] **TODO 2.1a** `Tip(str, Enum)`: `"venit"`, `"cheltuiala"`
- [ ] **TODO 2.1b** `CategorieTranzactie(str, Enum)`: 3 categorii de venit + 7 de cheltuială
- [ ] **TODO 2.1c** `TranzactieIn`: `descriere` 2–200 caractere, `suma` > 0,
  `data` cu `default_factory=date.today`

### 2.2 Abonament
- [ ] **TODO 2.2a** `CategorieAbonament(str, Enum)`: `Streaming`, `Muzica`, `Sport`,
  `Software`, `Telefon & Internet`, `Altele`
- [ ] **TODO 2.2b** `AbonamentIn`: `nume` 2–100 caractere, `cost_lunar` > 0, `zi_plata` 1–31

### 2.3 Chat (pentru `/chat`)
- [ ] **TODO 2.3a** `MesajChat`: `role` doar `"user"` / `"assistant"`, `content`
- [ ] **TODO 2.3b** `ChatIn`: `mesaj` (nu poate fi gol), `istoric` (implicit `[]`)
- [ ] **TODO 2.3c** `ApelTool`: `tool`, `argumente`, `rezultat`
- [ ] **TODO 2.3d** `ChatOut`: `raspuns`, `apeluri`

## Pasul 3 — `app.py` (API-ul FastAPI)

importurile, `init_db()`, `app = FastAPI(...)` și pornirea
serverului cu `uvicorn.run(...)` la finalul fișierului.

### 3.1 Tranzacții
- [ ] **TODO 3.1a** `GET /tranzactii?luna=&tip=&categorie=` — filtre opționale
  (`str | None = None`); lună greșită → `400`
- [ ] **TODO 3.1b** `POST /tranzactii` (201) — primește `TranzactieIn`
- [ ] **TODO 3.1c** `DELETE /tranzactii/{id}` — `404` dacă nu există

### 3.2 Abonamente
- [ ] **TODO 3.2a** `GET /abonamente`
- [ ] **TODO 3.2b** `POST /abonamente` (201) — **înainte** de salvare se verifică
  numele duplicat → `400`
- [ ] **TODO 3.2c** `PUT /abonamente/{id}/comuta` — `404` dacă nu există
- [ ] **TODO 3.2d** `DELETE /abonamente/{id}` — `404` dacă nu există

### 3.3 Sold
- [ ] **TODO 3.3** `GET /sold?luna=` — fără lună → luna curentă; lună greșită → `400`

### 3.4 Chat (după Pasul 4)
- [ ] **TODO 3.4** `POST /chat` — `ChatIn` → `ruleaza_agent(...)` → `ChatOut`;
  eroare de la OpenAI → `502`

**Test:** `python3 app.py` → http://127.0.0.1:8000/docs. Din `/docs`:
adaugă o tranzacție, cere `/tranzactii?luna=2026-13` (trebuie `400`),
adaugă de două ori același abonament (a doua oară `400`), cere `/sold`.

---

## Pasul 4 — `agent.py` (Consilierul AI)

- configurarea: `client = OpenAI()`, `MODEL`, `MAX_PASI`
- schema celor 7 tool-uri (lista `tools`) — din `description` decide
  modelul ce tool apelează:

  | tool | ce face | parametri |
  |------|---------|-----------|
  | `listeaza_tranzactii` | citire | `luna`, `tip`, `categorie` — opționale |
  | `adauga_tranzactie` | scriere, `strict` | `descriere`, `tip`, `categorie`, `suma`, `data` (sau `null`) |
  | `sterge_tranzactie` | scriere | `tranzactie_id` |
  | `listeaza_abonamente` | citire | — |
  | `adauga_abonament` | scriere, `strict` | `nume`, `categorie`, `cost_lunar`, `zi_plata` |
  | `comuta_abonament` | scriere | `abonament_id` |
  | `sold_luna` | citire | `luna` — opțional |

- funcțiile ajutătoare `tranzactie_dict`, `abonament_dict`, `erori_validare`
- dicționarul `FUNCTII`, `system_prompt()` și bucla `ruleaza_agent(...)`

### 4.3 Implementarea tool-urilor
Fiecare funcție primește `db` + argumentele modelului și întoarce un
**string**. Erorile se întorc ca text (nu ca excepții), ca modelul să le
poată explica utilizatorului.
- [ ] **TODO 4.3a** `listeaza_tranzactii` → JSON cu lista **și totalul**
  (un LLM greșește la adunări — Python calculează)
- [ ] **TODO 4.3b** `adauga_tranzactie` → validare cu `TranzactieIn`, apoi salvare
- [ ] **TODO 4.3c** `sterge_tranzactie` → mesaj de eroare dacă nu există
- [ ] **TODO 4.3d** `listeaza_abonamente` → JSON cu lista + `total_lunar_active`
- [ ] **TODO 4.3e** `adauga_abonament` → validare cu `AbonamentIn` + nume duplicat
- [ ] **TODO 4.3f** `comuta_abonament` → „Abonamentul X e acum activ / pus pe pauză”
- [ ] **TODO 4.3g** `sold_luna` → fără lună → luna curentă

## Pasul 5 — `comun.py` + `ui.py`

- `comun.py` — funcția `api(metoda, cale, ...)` folosită de toate paginile.
- `ui.py` — meniul aplicației: câte un `st.Page` pentru fiecare pagină
  din `pagini/`, apoi `st.navigation([...]).run()`.

## Pasul 6 — `pagini/` 

### 6.1 `tranzactii.py`
- [ ] **TODO 1** dicționarul `params` cu filtrele (luna, tip) — cheia se
  adaugă doar dacă filtrul are o valoare; `"Toate"` = fără filtru
- [ ] **TODO 2** totalul veniturilor și al cheltuielilor, cu un `for`

### 6.2 `adauga.py`
- [ ] **TODO** formularul (descriere, categorie din `CATEGORII[tip]`, sumă,
  dată) și `POST /tranzactii` la submit; data trimisă cu `.isoformat()`

### 6.3 `abonamente.py`
- [ ] **TODO 1** butonul Pauză / Activează → `PUT /abonamente/{id}/comuta` + `st.rerun()`
- [ ] **TODO 2** formularul „Abonament nou” → `POST /abonamente`

### 6.4 `dashboard.py`
- [ ] **TODO 1** procentul din venituri cheltuit (bara de progres), cu
  cele două cazuri speciale: venituri 0 și procent peste 100%
- [ ] **TODO 2** dicționarul `categorie → total` pentru graficul cheltuielilor

### 6.5 `consilier.py`
- [ ] **TODO** mesajul nou: afișare → istoric (doar `role` + `content`) →
  `POST /chat` cu `timeout=60` → afișarea răspunsului → salvarea ambelor
  mesaje în `st.session_state.messages`

---
