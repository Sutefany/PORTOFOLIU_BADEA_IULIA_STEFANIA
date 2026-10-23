# PROIECT PERSONAL — Aplicatie pentru extragerea, validarea si gestionarea automata a datelor unor procese verbale

## IPOTEZA PROIECTULUI => caz real
Pana acum:
- procesele verbale erau date pe un grup de whatsapp compus din doua persoane:

| EXPEDITOR                                     | DESTINATAR                                          |
|-----------------------------------------------|-----------------------------------------------------|
| el trimite PV-urile                           | el primeste PV-urile                                |
| nu completeaza nicio valoare in tabelul Excel | trece manual datele scrise de mana in tabelul Excel |
| descarca excelul de pe grup                   | situatia generala de lucrari se genereaza automat   |
| trimite situatia generala mai departe         | trimite excelul pe grupul de Whatsapp               |

- PROBLEME OBSERVATE:
 
- greseli de trecere in tabel (neatentie, graba, abundenta cifrelor etc.)
- nu exista o baza de date in care sa fie stocate permanent
- nu exista un model de parsare a datelor (pot fi interpretate gresit de la angajat la angajat)
- nu exista un centralizator/ filtru de informatii (Excel diferit de la saptamana la saptamana -> fara sinteza generala)

## DESCRIEREA PROIECTULUI

- [ ] Realizarea unei INTERFETE WEB STREAMLIT in care utilizatorul sa introduca manual sau cu ajutorul agentului datele
de pe procesele verbale sau sa ataseze o fotografie (format pdf) a procesului verbal. 
- [ ] Textul scris de mana va fi decodificat in Python fara a accesa AI-ul (rol: siguranta a datelor), se va completa 
baza de date si se vor realiza si completa documentele excel conform cerintelor modelului anexat. 
- [ ] Manual sau prin intermediul Agentului AI, utilizatorul poate sa adauge, sa stearga sau sa modifice un proces verbal. 
- [ ] Sinteza unor informatii din baza de date poate fi ceruta cerandu-i cu limbaj propriu Agentului AI 
(ex: Care echipa a facut cei mai multi km in ziua "X"? etc.). 
- [ ] La final, documentul Excel creat cu datele respective poate fi descarcat si verificat manual (pentru siguranta si
pentru evitarea erorilor de decodificare a scrisului de mana). 
- [ ] Modelul documentului Excel este deja dat (o singura foaie drept model), iar aplicatia trebuie sa creeze un sheet 
per echipa si sa completeze zilnic conform datei trecute pe PV. Un sheet contine un tabel pentru fiecare zi a saptamanii. 

## SCHEMA GENERALA A PARCURSULUI PROIECTULUI

                                ┌─────────────────────┐
                                │     SURSE DATE      │
                                │                     │
                                │  WhatsApp group,    │  # fara conectare pe WhatsApp -> preluarea pdf-urilor
                                │  manual, agent      │  # prin interfata Streamlit
                                │       sau           │
                                │   Upload PDF-uri    │  # atasarea documentelor in Streamlit
                                └──────────┬──────────┘
                                           │
                                           ▼
                                ┌─────────────────────┐
                                │       OCR           │  # citirea pdf-urilor / jpg-urilor create
                                │     RapidOCR        │
                                │                     │
                                │ PDF → text brut     │  # textul sub forma de dictionar relevant {echipa: {cod: valoare}}
                                └──────────┬──────────┘
                                           │
                                           ▼
                                ┌─────────────────────┐
                                │      OPENAI         │
                                │                     │
                                │ Interpretare        │  # AI-ul nu inventeaza, ci cere datele valabile pentru completarea
                                │ Extracție date      │  # bazei de date si, implicit, excel-urilor
                                │ Asociere coduri     │
                                │ Tool-uri            │
                                └──────────┬──────────┘
                                           │
                                           ▼
                                ┌─────────────────────┐
                                │      PYDANTIC       │
                                │                     │
                                │ Validare            │  # validarea oricaror date de intrare in baza de date 
                                │ Tipuri              │  # pentru evitarea duplicatelor, confuziei de date
                                │ Câmpuri obligatorii │
                                └──────────┬──────────┘
                                           │
                                     valid │ invalid
                                          /   \
                                         /     \
                                        ▼       ▼
                                     DUPLICATE  REVIEW   # orice eroare este sugestiva in interfata Streamlit
                                     CHECK      MANUAL
                                        │
                                        ▼
                                ┌─────────────────────┐
                                │     DATABASE        │
                                │                     │
                                │ DataGrip            │  # date insiruite -> filtrare prin interfata sau in SQL
                                │ (interfață DB)      │
                                └──────────┬──────────┘
                                           │
                                           ▼
                                ┌─────────────────────┐
                                │       EXCEL         │  # stergere existent si refacere cf. cerintelor -> evitare duplicate
                                │                     │  # informatii preluate din baza de date -> completare in Excel
                                │ Tabele finale       │  # posibilitatea de descarcare a documentelor la alegere in Streamlit
                                └─────────────────────┘

# PASUL 0 - configurare_db.py - fisier cu username, parola, cheie api (pentru siguranta accesului)

# PASUL 1 - 1.model.py ← baza de date (tabele + funcții specifice - afisare, adaugare, stergere, modificare, sume)

### PARTEA 0 - CONEXIUNEA LA MySQL - username si password neafisate din session28.date

### PARTEA 1A - MODELELE/ TABELE in DataGrip: Sablon + ProceseVerbale

TODO 1.a: clasa Sablon (mosteneste Base) => id, cod, descriere (MODEL EXISTENT PE HARTIE TRECUT IN DB CA SABLON)

TODO 1.b - clasa ProceseVerbale (mosteneste Base) => id, echipa, cod, descriere, valori, data (descriere dependenta de Sablon)

### PARTEA 1B - PORNIREA BAZEI DE DATE

TODO 1.c: reset_db() => sterge TOT si porneste cu tabele goale

TODO 1.d: adauga_date_sablon(s) => se creeaza sablonul de unde va fi preluata descrierea dupa cod

TODO 1.e: construieste_pv(s, echipa, cod, valori, data) => ProceseVerbale preia descrierea din Sablon + initializare db

TODO 1.f: adauga_date_testare(s) - DOAR TESTARE => va fi comentata ulterior dupa verificarea functionalitatii (date ipotetice)

### PARTEA 1C - CRUD ProceseVerbale

TODO 1g: adauga_pv(s, echipa, cod, valori, data) => functie pentru adaugarea unui nou pv

TODO 1h: toate_pv(s, echipa, cod=None, data=None) => afisare informatii pv (toate sau filtrate)

TODO 1i: sterge_pv(s, pv_echipa, pv_data) => va sterge TOT PROCESUL VERBAL din ziua respectiva

TODO 1j: sterge_dupa_id(s, id) => va sterge UN SINGUR ELEMENT dupa id-ul introdus

TODO 1k: modificare_pv(s, id, echipa_noua, cod_nou, valoare_noua) => poate schimba toti parametri unui pv gresit 
(inafara de descriere care este dependenta de cod si se modifica automat)

TODO 1l: total_km(s, pv_echipa, pv_data) => suma km a echipei si datei selectate (COP11, COP13, COP20, COP27, COP28, COP29)

TODO 1m: total_dupa_cod(s, echipa, cod, data) => calculul sumei valorilor unei echipe din data selectata in functie de cod

### PARTEA FINALA - get_db() - evitarea apelarii functiei la fiecare sesiune deschisa, salvata, inchisa

Functia get_db() => apelare doar la cerere, scriere o singura data pentru eliminarea codului redundant

# PASUL 2 - 2.schema.py ← ce date sunt acceptate de la client (validare)

TODO 2a: clasa Cod_Permis(str, Enum) => categoriile permise (COP1 - COP29)

TODO 2b: clasa PvIn(BaseModel) => validarea datelor noi primite de la client sau de la agent (echipa, cod, valori, data)

TODO 2c: clasa MesajChat(BaseModel) => UN mesaj din istoric

TODO 2d: clasa ChatIn(BaseModel) => ce primeste POST /chat

TODO 2e: clasa ApelTool(BaseModel) => UN tool apelat de agent

TODO 2f: clasa ChatOut(BaseModel) => ce intoarce POST /chat

# PASUL 3 - 3.app.py ← rutele HTTP (folosesc model + schema)

### PARTEA 3A - PROCESE VERBALE

TODO 3a: GET /procese_verbale => lista proceselor verbale

TODO 3b: POST /adauga_procese_verbale => adaugarea unui proces verbal (element cu element)

TODO 3c: DELETE /sterge_proces_verbal => sterge un proces verbal (TOATE VALORILE DIN ZIUA RESPECTIVA ALE ECHIPEI ALESE)

TODO 3d: DELETE /sterge_pv => sterge un element din baza de date

TODO 3e: PUT /modifica_proces_verbal => actualizare dupa id => VALOARE, COD, DATA si/sau ECHIPA

### PARTEA 3B - TOTAL_KM/ ZI, ECHIPA si TOTAL_DUPA_COD

TODO 3f: GET/total_km => nr. total de kilometri intr-o zi a unei echipe (dupa data si coduri specifice)

TODO 3g: GET/total_cod => nr. total de kilometri intr-o zi a unei echipe (dupa data si un cod ales)

### PARTEA 3C - chat: CONSILIERUL AI

TODO 3h: POST /chat => trimite mesajul utilizatorului la agent

# PASUL 4 - 4.agent.py ← consilierul AI (folosește model + schema)

### PARTEA 4A - DATE DESPRE AI

TODO 4a: alegerea modelului si AI-ului + preluare cheie api de pe platforma aferenta AI-ului

TODO 4b: realizarea tool-urilor ajutatoare pentru accesarea functiilor

### PARTEA 4B - IMPLEMENTAREA TOOL-URILOR

TODO 4c: listeaza_task_uri -> lista_pv, rezultat ca JSON

TODO 4d: adauga_proces_verbal -> rezultat ca JSON

TODO 4e: sterge_proces_verbal 

TODO 4f: sterge_id 

TODO 4g: sterge_id 

TODO 4h: modifica_proces_verbal

TODO 4i: total_cod 

TODO 4j: listarea functiilor

TODO 4k: SYSTEM- definirea rolului si comportamentului AI-ului

TODO 4l: ruleaza_agent(db, mesaj, istoric)

# PASUL 5 - 5.ui.py + 5.comun.py ← scheletul interfeței Streamlit

### 5.comun.py - "MESAGERUL" dintre STREAMLIT si API-ul aplicatiei

### 5.ui.py - PAGINILE DIN STREAMLIT + NAVIGARE

CONFIGURAREA PAGINII PRINCIPALE- titlu, icon, layout

CONFIGURAREA PAGINILOR - pagina_ROL: listare, adaugare, modificare si stergere, asistent - localizare folder, titlu, icon, 
                                     generare si descarcare excel-uri

NAVIGARE PRIN PAGINI

# PASUL 6 - pages/*.py ← paginile (ADAUGA, STERGE, MODIFICA, ASISTENT_AI, GENEREAZA SI DESCARCA EXCEL)

listare.py => PAGINA DE LISTARE/ FILTRARE (+ total_km (filtru: echipa, data), total_dupa_cod (filtru: echipa, cod, data))

adauga.py => PAGINA DE ADAUGARE PROCES VERBAL

modifica_sterge.py => PAGINA DE MODIFICARE/ STERGERE PROCESE VERBALE

asistent.py => PAGINA ASISTENT AI

descarca_excel => PAGINA DE GENERARE SI DESCARCARE EXCEL LA ALEGERE

# PASUL 7 - 7.ocr.py ← extragerea textului din imaginile jpg

### PARTEA 7A - LEGATURA CU FOLDERUL IMPLICIT + SABLOANE + pornirea OCR-ului LOCAL

TODO 7a: crearea unei cai catre folderul "uploads" unde se afla pdf-urile salvate

TODO 7b: listarea codurilor -> viitor sablon

TODO 7c: stabilirea coordonatelor tabelului

TODO 7d: pornirea RapidOCR local

### PARTEA 7B - PREGATIREA PENTRU OCR - transformare pdf in imagine, pixeli albastri in casuta <=> completat, aranjarea celulei

TODO 7e: transformarea pdf-ului in imagine

TODO 7f: extragerea scrisului albastru -> COMPLETARE OBLIGATORIE CU PIX ALBASTRU

TODO 7g: decuparea celulei completate

TODO 7h: pregatirea celulei -> marire, masca alba pentru a evita confuzia cu marginile celulei

### PARTEA 7C - CITIRE - o celula, un tabel

TODO 7i: citirea unei celule

TODO 7j: citirea tabelului intreg

### PARTEA 7D - PROGRAMUL PRINCIPAL

# PASUL 8 - 8.procesator.py ← PROCESATOR DATE IMAGINI- validarea si constructia datelor citite de ocr + adaugarea in db

TODO 8A: functia adaugare_db_poze(nume_pdf, data) -> numele echipei si data vor fi luate din Streamlit

# PASUL 9 - 9.excel.py ← completare Excel cu datele preluate (+ model.xlsx si exports/*)

### PARTEA 9 - NORMALIZAREA DATEI DIN BAZA DE DATE

TODO 9a: stergerea tuturor tabelelor - la fiecare rulare trebuie sterse si refacute pt. evitarea duplicatelor

TODO 9b: stabilirea zilei de luni si de sambata pentru marcarea distinctiva a titlului

### PARTEA 9B - REALIZAREA TABELELOR EXCEL, PRELUAREA INFORMATIEI SI COMPLETAREA TABELELOR

TODO 9c: deschiderea sesiunii pentru a prelua datele din baza de date (parcurgerea tuturor datelor)

TODO 9d: realizarea excelului caracteristic fiecarei saptamani - SITUATIA GENERALA DE LUCRARI 12-10-2026 - 16-10-2026.xlsx

TODO 9e: stabilirea suprafetei de lucru: fisier caracteristic, ce foi se vor completa, redenumirea foilor

TODO 9f: completarea propriu-zisa in tabelele excel- completarea datelor

TODO 9g: completarea propriu-zisa in tabelele excel- completarea cu valorile returnate de db in functie de cod

TODO 9h: salvare fisier excel

# PASUL 10 - model_excel ← model Excel primit (sablon) - model.xlsx

# PASUL 11 - uploads/* ← fisierele JPG incarcate in Streamlit si de pe Whatsapp (FOLDER)

## PASUL 12 - exports/* ← fisierele Excel generate - un fisier/saptamana (FOLDER)

