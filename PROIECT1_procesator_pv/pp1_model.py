
############################### CREAREA BAZEI DE DATE - tabele + functii ###############################

### IMPORTURI NECESARE

from datetime import date

from sqlalchemy import create_engine, String, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

from configurare_db import username, password

# ###################################################################################
# PARTEA 0 - CONEXIUNEA LA MySQL - username si password neafisate din configurare_db
# ###################################################################################

engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost:3306/proiect_personal")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# ###################################################################################
# PARTEA 1A - MODELELE/ TABELE in DataGrip: Sablon + ProceseVerbale
# ###################################################################################

#   - Sablon  -> un tabel cu id propriu, codurile si descrierea aferenta fiecarui cod
#   (ex: 1. COP1 - EPUIZAREA MECANICA A APEI CU MOTOPOMPA)
#   - ProceseVerbale  -> un tabel cu id propriu, codurile, descrierea (dependenta de sablon),
#   valorile si data prezenta pe procesul verbal

# TODO 1.a: clasa Sablon (mosteneste Base)
#
#   1. __tablename__ = "pv_sablon"
#   2. coloanele, fiecare scrisa ca  nume: Mapped[tip] = mapped_column(...)
#        id              int     cheie primara (primary_key=True), autoincrement=True
#        cod             str     String(10)      ex: COP29 (unica)
#        descriere       str     String(100)    ex: "TRANSPORT MATERIALE MASINA 3.5 T" (unica)

# CONCEPT NOU: - legatura dintre clasa Sablon si clasa ProceseVerbale
#              - procese_verbale: Mapped[list["ProceseVerbale"]] = relationship(back_populates="sablon")

class Sablon(Base):
    __tablename__ = "pv_sablon"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cod: Mapped[str] = mapped_column(String(10), unique=True)
    descriere: Mapped[str] = mapped_column(String(100), unique=True)

    procese_verbale: Mapped[list["ProceseVerbale"]] = relationship(back_populates="sablon")

    def __str__(self):
        return (f"{self.id}.{self.cod} - {self.descriere}")

# TODO 1.b: clasa ProceseVerbale (mosteneste Base)
#
#   1. __tablename__ = "pv_total" - TOATE DATELE DIN PROCESELE VERBALE indiferent de echipa si data
#   2. coloanele, fiecare scrisa ca  nume: Mapped[tip] = mapped_column(...)
#        id              int     cheie primara (primary_key=True), autoincrement=True
#        echipa          str     String(50)      ex: Judet - NumeAngajat
#        cod             str     String(10)      ex: COP29
#        descriere       str     String(100)    ex: "TRANSPORT MATERIALE MASINA 3.5 T" - nu va mai fi apelata deoarece
#                                                   este preluata din tabelul Sablon
#        valori          float
#        data            date

class ProceseVerbale(Base):
    __tablename__ = "pv_total"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    echipa: Mapped[str] = mapped_column(String(50))
    cod: Mapped[str] = mapped_column(String(10), ForeignKey("pv_sablon.cod"))
    descriere: Mapped[str] = mapped_column(String(100))
    valori: Mapped[float]
    data: Mapped[date]

    sablon: Mapped["Sablon"] = relationship(back_populates="procese_verbale")    # permite accesarea pv.sablon.descriere

    def __str__(self):
        return (f"{self.id}.{self.echipa} -> {self.cod} - {self.descriere} -> {self.valori} ({self.data})")

# ###################################################################################
# PARTEA 1B - PORNIREA BAZEI DE DATE
# ###################################################################################

# TODO 1.c: reset_db() - sterge TOT si porneste cu tabele goale

def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

# reset_db() - APELARE O SINGURA DATA LA INCEPUT SA CREEZE TABELUL SI SA STEARGA CE EXISTA

# TODO 1.d: adauga_date_sablon(s) - se creeaza sablonul - descrierea va fi preluata dupa cod
# Adaugarea datelor fixe din tabelul Sablon - date fixe ce nu se vor schimba

def adauga_date_sablon(s):
    if not s.scalars(select(Sablon)).all():
        s.add_all([
            Sablon(cod="COP1", descriere="EPUIZAREA MECANICA A APEI CU MOTOPOMPA"),
            Sablon(cod="COP2", descriere="REFACERI PAVAJE LA STRAZI (TOATTE MATERIALELE, TRANSPORTURILE SI MANOPERA INCLUSE)"),
            Sablon(cod="COP3", descriere="REFACERI PAVAJE TROTUAR, ALEI PIETONALE (TOATE MATERIALELE, TRANSPORTURILE Sl MANOPERA INCLUSE)"),
            Sablon(cod="COP4", descriere="INCHIRIERE MACARA / NACELA"),
            Sablon(cod="COP5", descriere="TRANSPORT MATERIALE MASINA 1.5 T"),
            Sablon(cod="COP6", descriere="TRANSPORT MATERIALE MASINA 3.5 T"),
            Sablon(cod="COP8", descriere="TRANSPORT MATERIALE MASINA 20 T"),
            Sablon(cod="COP9", descriere="SPARGERE BETON -  CAROSABIL"),
            Sablon(cod="COP10", descriere="SPARGERE BETON -  FUNDATIE DRUM "),
            Sablon(cod="COP11", descriere="DEMONTARE CABLU DIN CANALIZARE MAI MIC SAU EGAL DE 600/0.4"),
            Sablon(cod="COP12", descriere="DEMONTARE CABLU DE TELECOM DE PE ZID"),
            Sablon(cod="COP13", descriere="DEMONTARE CABLU DE TELECOM. DE PE STALPI (MANOPERA DE DEMONTARE)"),
            Sablon(cod="COP14", descriere="DEMONTARE STREANG SAU BRIDA SAU SARMA RADIOFICARE"),
            Sablon(cod="COP15", descriere="DEMONTARE STALP DE LEMN OROC"),
            Sablon(cod="COP16", descriere="DEMONTARE  TRAVERSA (SUPORTI RADIOFICARE) CONSOLA"),
            Sablon(cod="COP17", descriere="DEMONTARE CUTIE TERMINALA"),
            Sablon(cod="COP18", descriere="DEMONTARE APARATOARE 'U' DE CABLU (50MM)"),
            Sablon(cod="COP20", descriere="DEMONTARE CABLU DIN CANALIZARE MAI MARE SAU EGAL DE 600/0.6"),
            Sablon(cod="COP21", descriere="Vidanjare camine "),
            Sablon(cod="COP23", descriere="Asistenta Tehnica (echipa 2 tehnicieni)"),
            Sablon(cod="COP24", descriere="INCHIRIERE BULDOEXCAVATOR SAU UTILAJ"),
            Sablon(cod="COP26", descriere="Inchiriere TIR cu ora ( pentru perioada de stationare pana la incarcarea completa)"),
            Sablon(cod="COP27", descriere="DEMONTARE CABLU + STREANG"),
            Sablon(cod="COP28", descriere="DEMONTARE CABLU + BRIDA SAU STREANG + BRIDA"),
            Sablon(cod="COP29", descriere="DEMONTARE CABLU + STREANG + BRIDA")
        ])
    s.commit()

# TODO 1.e: construieste_pv(s, echipa, cod, valori, data) - functie ajutatoare pentru preluarea descrierii

def construieste_pv(s, echipa, cod, valori, data):
    sablon = s.scalar(select(Sablon).where(Sablon.cod == cod))
    if sablon is None:
        raise ValueError(f"Codul {cod} nu exista in sablonul dat")
    return ProceseVerbale(echipa=echipa, cod=cod, descriere=sablon.descriere, valori=valori, data=data)

# TODO 1.f: adauga_date_testare(s) - testarea functionalitatii bazei de date si functiilor (adaugarea unor date ipotetice)

def adauga_date_testare(s):
    if not s.scalars(select(ProceseVerbale)).all():
        s.add_all([
            construieste_pv(s, echipa="Marius- Arges", cod="COP18", valori=12, data=date(2026, 10, 9)),
            construieste_pv(s,echipa="Marius- Arges", cod="COP16", valori=6, data=date(2026, 10, 9)),
            construieste_pv(s,echipa="Marius- Arges", cod="COP6", valori=35, data=date(2026, 10, 9)),
            construieste_pv(s,echipa="Marius- Arges", cod="COP27", valori=400, data=date(2026, 10, 9)),
            construieste_pv(s,echipa="Marius- Arges", cod="COP28", valori=100, data=date(2026, 10, 9)),
            construieste_pv(s,echipa="Marius- Arges", cod="COP29", valori=55, data=date(2026, 10, 9)),
            construieste_pv(s,echipa="Aurel- Prahova", cod="COP11", valori=1234, data=date(2026, 10, 8)),
            construieste_pv(s,echipa="Marius- Cluj", cod="COP16", valori=20, data=date(2026, 10, 9))
        ])
    s.commit()

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_sablon(s)
        # adauga_date_testare(s) #APELARE LA INCEPUT PENTRU ADAUGAREA DATELOR SI PE PARCURSUL TESTARII

# init_db() - APELARE DOAR LA INCEPUT PENTRU REALIZAREA SABLONULUI

# ###################################################################################
# PARTEA 1C - CRUD ProceseVerbale
# ###################################################################################

# TODO 1g: adauga_pv(s, echipa, cod, valori, data)
#  ATENTIE: pv_nou trebuie creat cu functia construieste_pv in care este apelata clasa ProcesVerbal!
#  -> rol: preluare descriere din sablon

def adauga_pv(s, echipa, cod, valori, data):
    pv = construieste_pv(s, echipa= echipa, cod=cod, valori=valori, data=data)
    s.add(pv)
    s.commit()
    return pv

# TESTARE FUNCTIE adauga_pv(s, echipa, cod, valori, data) - 3 valori, aceeasi echipa, aceeasi data, cod diferit sau duplicat
# with SessionLocal() as s:
#     pv_nou = adauga_pv(s, echipa= "Vici- Olt", cod="COP2", valori= 1.5, data=date(2026, 10, 9))
#     s.add(pv_nou)
#     s.commit()
#     print("Gata")
#
# with SessionLocal() as s:
#     pv_nou = adauga_pv(s, echipa= "Vici- Olt", cod="COP11", valori= 1.5, data=date(2026, 10, 9))
#     s.add(pv_nou)
#     s.commit()
#     print("Gata")
#
# with SessionLocal() as s:
#     pv_nou = adauga_pv(s, echipa= "Vici- Olt", cod="COP23", valori= 1.5, data=date(2026, 10, 9))
#     s.add(pv_nou)
#     s.commit()
#     print("Gata")
#
# with SessionLocal() as s:
#     pv_nou = adauga_pv(s, echipa= "Marius- Arges", cod="COP6", valori= 33, data=date(2026, 10, 9))
#     s.add(pv_nou)
#     s.commit()
#     print("Gata")

# TODO 1h: toate_pv(s, echipa, cod=None, data=None)
#  Intoarce o LISTA de obiecte. Cele 3 filtre sunt optionale (ce este None se ignora):
#       toate_pv(s)                                                                       -> toate
#       toate_pv(s, echipa="Marius- Olt")                                                 -> doar cele ale echipei "Marius- Olt"
#       toate_pv(s, cod="COP29")                                                          -> doar cele cu codul COP29
#       toate_pv(s, data="2026-10-09")                                                    -> doar cele din data respectiva
#       toate_pv(s, echipa="Marius- Olt", cod="COP29", "2026-10-09")                      -> toate filtrele aplicate
#  ATENTIE: CODUL se va sorta astfel: COP1, COP13, COP16, COP29, COP6 (dupa prima cifra)  -> trebuie modificat

def toate_pv(s, echipa=None, cod=None, data=None):
    query = select(ProceseVerbale)
    if echipa:
        query = query.where(ProceseVerbale.echipa == echipa)
    if cod:
        query = query.where(ProceseVerbale.cod == cod)
    if data:
        query = query.where(ProceseVerbale.data == data)
    lista_query = s.scalars(query).all()
    return lista_query

# TESTARE FUNCTIE toate_pv(s, echipa=None, cod=None, data=None)
# with SessionLocal() as s:
#     toate = toate_pv(s, echipa="Marius- Arges", cod=None, data=date(2026, 10, 9))
#     for pv in toate:
#         print(f"{pv.data} => {pv.id}.{pv.echipa} => {pv.cod} - {pv.descriere} ==== {pv.valori}")
#     print()
#     toate_2 = toate_pv(s, echipa="Marius- Arges", cod="COP6", data=date(2026, 10, 9))
#     for pv in toate_2:
#         print(f"{pv.data} => {pv.id}.{pv.echipa} => {pv.cod} - {pv.descriere} ==== {pv.valori}")

# TODO 1i: sterge_pv(s, pv_echipa, pv_data)
#   Intoarce True daca a sters toate datele echipei din data respectiva, False daca nu exista.
#   va sterge TOT PROCESUL VERBAL din data 'X' al echipei selectate, nu doar o valoare
#   valorile se pot modifica individual cu functia de mai jos: modificare_pv(s, pv_id, pv_cod=None, valoare_noua=None)

def sterge_pv(s, echipa, data):
    pv = select(ProceseVerbale).where(ProceseVerbale.echipa == echipa, ProceseVerbale.data == data)
    lista_pv_filtru = s.scalars(pv).all()
    if not lista_pv_filtru:
        return False
    for p in lista_pv_filtru:
        s.delete(p)
    s.commit()
    return True

# TESTARE FUNCTIE sterge_pv(s, echipa, data)
# with SessionLocal() as s:
#     sters = sterge_pv(s, "Vici- Olt", "2026-10-09")
#     s.commit()
#     print(sters)

# TODO 1j: sterge_dupa_id(s, id)
#  va returna True daca a sters elementul cu id-ul dat sau False daca nu il gaseste
#  va sterge doar o valoare din tabel (ex: AI-ul trece gresit unele valori in plus)

def sterge_dupa_id(s, pv_id):
    pv = s.get(ProceseVerbale, pv_id)
    if not pv:
        return False
    s.delete(pv)
    s.commit()
    return True

# TESTARE FUNCTIE sterge_dupa_id(s, id)
# with SessionLocal() as s:
#     pv_sters = sterge_dupa_id(s, 15)
#     s.commit()
#     print("Gata")

# TODO 1k: modificare_pv(s, id, echipa_noua, cod_nou, valoare_noua=None)
#   Schimba VALOAREA elementului cu id-ul respectiv
#                     SI/SAU
#   Schimba CODUL elementului cu id-ul respectiv
#                     SI/SAU
#   Schimba NUMELE ECHIPEI elementului cu id-ul respectiv
#   ATENTIE: pentru a schimba descrierea va trebui cautat in sablon elementul cu codul nou introdus, preluarea descrierii
#   si sa fie pusa in PV-ul in care doar codul a fost modificat. Valoarea modificata nu influenteaza textul descrierii!

def modificare_pv(s, pv_id, echipa_noua, cod_nou, data_noua, valoare_noua):
    pv = s.get(ProceseVerbale, pv_id)
    if pv is None:
        return None
    pv.echipa = echipa_noua
    pv.data = data_noua
    pv.valori = valoare_noua
    if pv.cod != cod_nou:
        pv.cod = cod_nou
        obiect_nou = construieste_pv(s, echipa=pv.echipa, cod=pv.cod, valori=pv.valori, data=pv.data)
        pv.descriere = obiect_nou.descriere                    # pentru a lua descrierea de la codul nou din SABLON
    s.commit()
    return pv

# TESTARE FUNCTIE modificare_pv(s, id, echipa_noua, cod_nou, valoare_noua=None)
# with SessionLocal() as s:
#     modificare_pv(s, 2, echipa_noua="Marius- Arges", cod_nou= "COP1", valoare_noua=3, data_noua="2026-10-07")
#     modificare_pv(s, 2, echipa_noua="Marian- Arges", cod_nou="COP11", valoare_noua=6, data_noua="2026-10-07")
#     modificare_pv(s, 2, echipa_noua="Marian- Arges", cod_nou="COP11", valoare_noua=3, data_noua="2026-10-07")
#     s.commit()
#     print("Gata")

# TODO 1l: total_km(s, pv_echipa, pv_data)
#   Calculul totalului de kilometri realizati pe data respectiva
#   Se iau in considerare doar codurile COP11, COP13, COP20, COP27, COP28, COP29
#   Daca nu se gaseste nicio informatie in baza de date -> Nu exista informatii despre echipa din ziua respectiva

def total_km(s, echipa, data):
    lista_pv = toate_pv(s, echipa=echipa, data=data)
    suma = 0
    if not lista_pv:
        return f"Nu exista informatii despre echipa din ziua respectiva"
    for pv in lista_pv:
        if pv.cod in ["COP11", "COP13", "COP20", "COP27", "COP28", "COP29"]:
            suma += pv.valori
    return int(suma) # toate valorile sunt declarate ca float pentru usurinta, dar numarul de km va fi intreg mereu

# TESTARE FUNCTIE total_km(s, pv_echipa, pv_data)
# with SessionLocal() as s:
#     suma = total_km(s, echipa="Marius- Arges", data=date(2026, 10, 9))
#     print(suma) #555
#     suma_2 = total_km(s, echipa="Marius- Cluj", data=date(2026, 10, 9))
#     print(suma_2)  #0 (nu exista coduri care sa se ia in considerare la suma)
#     suma_3 = total_km(s, echipa="Marius- Cluj", data=date(2026, 10, 5))
#     print(suma_3)  # Nu exista informatii despre echipa din ziua respectiva (nu exista data)
#     suma_3 = total_km(s, echipa="Marius- Alba", data=date(2026, 10, 5))
#     print(suma_3)  # Nu exista informatii despre echipa din ziua respectiva (nu exista data si echipa)

# TODO 1m: total_dupa_cod(s, echipa, cod, data)
#  Calculul sumei valorilor unei echipe din data selectata in functie de cod

def total_dupa_cod(s, echipa, cod, data):
    lista_pv = toate_pv(s, echipa=echipa, cod=cod, data=data)
    suma = 0
    if not lista_pv:
        return f"Nu exista informatii despre echipa din ziua respectiva"
    for pv in lista_pv:
        suma += pv.valori
    return suma

# TESTARE FUNCTIE total_dupa_cod(s, echipa, cod, data)
# with SessionLocal() as s:
#     suma = total_dupa_cod(s, echipa="Marius- Arges", cod="COP27", data=date(2026, 10, 9))
#     print(suma) #400.0
#     suma = total_dupa_cod(s, echipa="Marius- Arges", cod="COP6", data=date(2026, 10, 9))
#     print(suma)  #68.0

# ###################################################################################
# PARTEA FINALA - get_db() - evitarea apelarii functiei la fiecare sesiune deschisa, salvata, inchisa
# ###################################################################################

def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()

























