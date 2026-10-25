# Proiectul 1 — Mentor de carieră IT

## Tema

Tranziția spre o carieră în IT ridică multe întrebări practice: cum arată un CV
bun pentru un junior, cum te pregătești de interviu, cum negociezi salariul,
ce rol ți se potrivește, cum treci de primele luni la job. Informația există,
dar e împrăștiată în articole, video-uri și sfaturi contradictorii.

**Mentorul de carieră IT** adună această informație într-o bibliotecă de
ghiduri și pune peste ea un asistent AI care răspunde la întrebări **doar pe
baza ghidurilor** — cu sursa fiecărui răspuns.

## Cui se adresează

Persoanelor de 25–40 de ani care se reorientează spre IT: au experiență în alt
domeniu, învață programare și se pregătesc de primul job tehnic. Adică exact
voi. Aplicația pe care o construiți o puteți folosi apoi pentru propria
căutare de job.

## Ce face aplicația

1. **Păstrează ghidurile de carieră** într-o bază de date MySQL — fiecare ghid
   are titlu, categorie și conținut.
2. **Permite adăugarea și ștergerea ghidurilor** dintr-o interfață web. Un ghid
   nou devine imediat cautabil.
3. **Caută după sens**, nu după cuvinte: întrebarea „cum cer mai mulți bani la
   angajare?” găsește ghidul *Negocierea salarială*, deși cuvintele diferă.
4. **Răspunde ca un mentor**: asistentul AI caută ghidurile potrivite, le citește
   și formulează un sfat concret, aplicat pe situația utilizatorului — și spune
   din ce ghid a luat informația.
5. **Nu inventează**: dacă ghidurile nu acoperă o întrebare, mentorul spune
   asta, în loc să dea un răspuns plauzibil, dar neverificat.

## Paginile aplicației

| Pagină | Ce face | Ce parte din RAG |
|---|---|---|
| 📚 **Ghiduri** | lista ghidurilor, filtru pe categorie, conținutul fiecărui ghid, ștergere | — (date) |
| ➕ **Adaugă ghid** | formular: titlu, categorie, conținut; ghidul e salvat și indexat | — (date) |
| 🔎 **Căutare** | caută ghidurile după sens și arată distanța; **fără** modelul de chat | doar **R** |
| 🧭 **Mentor AI** | chat cu mentorul; sub fiecare răspuns, sursele folosite | **R + A + G** (RAG complet) |

## Cum funcționează

```
              ┌──────── MySQL ────────┐
  Ghiduri ──► │ tabela s50_ghid       │  ← sursa de adevăr
              └───────────────────────┘
                         │ la pornire + la fiecare adăugare/ștergere
                         ▼
              ┌──────── Chroma ───────┐
              │ aceleași ghiduri,     │  ← indexul pentru căutare după sens
              │ cu embedding-uri      │
              └───────────────────────┘
                         ▲
  Mentor AI ── /chat ── agent ── cauta_in_ghiduri  →  modelul scrie răspunsul
  Căutare ──── /cauta ───────────┘                     (doar rezultatele căutării)
```

## Ghidurile inițiale

Aplicația pornește cu 8 ghiduri (folderul `ghiduri_initiale/`):

| Ghid | Categorie |
|---|---|
| CV-ul pentru primul job în IT | CV și portofoliu |
| Portofoliul pe GitHub | CV și portofoliu |
| LinkedIn și networking | CV și portofoliu |
| Interviul comportamental și metoda STAR | Interviu |
| Interviul tehnic pentru juniori | Interviu |
| Negocierea salarială | Negociere |
| Roluri în IT pentru cei care încep | Roluri IT |
| Primele 90 de zile la primul job în IT | La job |

## Exemple de întrebări

| Întrebare | Comportament așteptat |
|---|---|
| „Ce răspund dacă mă întreabă care e cel mai mare defect al meu?” | sfat din *Interviul comportamental*; sursa afișată |
| „Am lucrat 5 ani în contabilitate. Ce rol din IT mi s-ar potrivi?” | recomandă *Data analyst* și explică de ce; sursa *Roluri în IT* |
| „Cum cer mai mulți bani când primesc oferta?” | pași din *Negocierea salarială* (interval, ofertă în scris, contraofertă) |
| „Ce pun în README la proiectele mele?” | lista din *Portofoliul pe GitHub* |
| „Cum devin pilot de avion?” | spune că ghidurile nu acoperă subiectul — **nu inventează** |

## Atenție

Ghidurile conțin sfaturi generale de carieră, scrise în scop educativ. Cifrele
de pe piața muncii și practicile de recrutare diferă între companii și se
schimbă în timp — verificați informația pentru situația voastră concretă.
