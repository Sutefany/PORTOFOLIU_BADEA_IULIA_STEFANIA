from datetime import date, timedelta

from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from session28.date import username, password

# #############################################################
# PARTEA 0 - CONEXIUNEA LA MySQL  (plan: 1.1)
# #############################################################

engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost:3306/curs")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# #############################################################
# PARTEA 1 - MODELELE: Tranzactie, Abonament  (plan: 1.2)
# #############################################################

class Tranzactie(Base):
    __tablename__ = "s45_tranzactie"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descriere: Mapped[str] = mapped_column(String(200))
    tip: Mapped[str] = mapped_column(String(20))
    categorie: Mapped[str] = mapped_column(String(30))
    suma: Mapped[float]
    data: Mapped[date]

    def __str__(self):
        return (f"Tranzactie #{self.id}: {self.tip} {self.suma} lei - {self.descriere} "
                f"({self.categorie}, {self.data})")


class Abonament(Base):
    __tablename__ = "s45_abonament"

    id:         Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    nume:       Mapped[str]   = mapped_column(String(100), unique=True)
    categorie:  Mapped[str]   = mapped_column(String(50))
    cost_lunar: Mapped[float]
    zi_plata:   Mapped[int]
    activ:      Mapped[bool]  = mapped_column(default=True)

    def __str__(self):
        if self.activ:
            stare = "activ"
        else:
            stare = "pe pauza"
        return (f"Abonament #{self.id}: {self.nume} - {self.cost_lunar} lei/luna, "
                f"plata pe {self.zi_plata} ({stare})")



# #############################################################
# PARTEA 1b - PORNIREA BAZEI DE DATE  (plan: 1.3)
# #############################################################

def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def adauga_date_initiale(s):
    azi = date.today()
    luna_asta = azi.replace(day=1)
    luna_trecuta = (luna_asta - timedelta(days=1)).replace(day=1)

    if not s.scalars(select(Tranzactie)).all():
        s.add_all([
            Tranzactie(descriere="Salariu",          tip="venit",      categorie="salariu",   suma=6500, data=luna_trecuta.replace(day=10)),
            Tranzactie(descriere="Chirie",           tip="cheltuiala", categorie="locuinta",  suma=2000, data=luna_trecuta.replace(day=12)),
            Tranzactie(descriere="Cumparaturi Lidl", tip="cheltuiala", categorie="mancare",   suma=620,  data=luna_trecuta.replace(day=18)),
            Tranzactie(descriere="Salariu",          tip="venit",      categorie="salariu",   suma=6500, data=luna_asta.replace(day=1)),
            Tranzactie(descriere="Proiect freelance", tip="venit",     categorie="freelance", suma=1200, data=luna_asta.replace(day=2)),
            Tranzactie(descriere="Chirie",           tip="cheltuiala", categorie="locuinta",  suma=2000, data=luna_asta.replace(day=2)),
            Tranzactie(descriere="Cumparaturi Mega", tip="cheltuiala", categorie="mancare",   suma=380,  data=luna_asta.replace(day=3)),
            Tranzactie(descriere="Abonament STB",    tip="cheltuiala", categorie="transport", suma=80,   data=luna_asta.replace(day=3)),
            Tranzactie(descriere="Factura curent",   tip="cheltuiala", categorie="facturi",   suma=210,  data=luna_asta.replace(day=4)),
            Tranzactie(descriere="Cina in oras",     tip="cheltuiala", categorie="distractie", suma=160, data=luna_asta.replace(day=5)),
        ])
    if not s.scalars(select(Abonament)).all():
        # aceleasi abonamente ca la s30
        s.add_all([
            Abonament(nume="Netflix",          categorie="Streaming",          cost_lunar=55.0,  zi_plata=5),
            Abonament(nume="Spotify",          categorie="Muzica",             cost_lunar=27.0,  zi_plata=12),
            Abonament(nume="Sala World Class", categorie="Sport",              cost_lunar=250.0, zi_plata=1),
            Abonament(nume="iCloud 200GB",     categorie="Software",           cost_lunar=15.0,  zi_plata=20),
            Abonament(nume="Digi mobil",       categorie="Telefon & Internet", cost_lunar=40.0,  zi_plata=25),
            Abonament(nume="HBO Max",          categorie="Streaming",          cost_lunar=30.0,  zi_plata=18, activ=False),
        ])
    s.commit()


def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)

init_db()
# #############################################################
# PARTEA 2 - CRUD Tranzactie  (plan: 1.4)
# #############################################################

def interval_luna(luna: str):
    an = int(luna[:4]) # primele 4 caractere din string reprezinta anul
    lu = int(luna[5:])

    inceput = date(an, lu, 1)

    if lu == 12:
        sfarsit = date(an + 1, 1, 1)
    else:
        sfarsit = date(an, lu +1, 1)
    return inceput, sfarsit


def luna_curenta() -> str:
    return date.today().strftime("%Y-%m")

def adauga_tranzactie(s, descriere, tip, categorie, suma, data):
    t = Tranzactie(descriere=descriere, tip=tip, categorie=categorie, suma=suma, data=data)
    s.add(t)
    s.commit()
    return t

def toate_tranzactiile(s, luna=None, tip=None, categorie=None):
    query = select(Tranzactie)
    if luna:
        inceput, sfarsit = interval_luna(luna)
        query = query.where(Tranzactie.data >= inceput, Tranzactie.data < sfarsit)
    if tip:
        query = query.where(Tranzactie.tip == tip)
    if categorie:
        query = query.where(Tranzactie.categorie == categorie)
    query = query.order_by(Tranzactie.data.desc(), Tranzactie.id.desc())
    return s.scalars(query).all()

def sterge_tranzactie(s, tranzactie_id):
    t = s.get(Tranzactie, tranzactie_id)
    if t is None:
        return False
    s.delete(t)
    s.commit()
    return True


# #############################################################
# PARTEA 3 - CRUD Abonament  (plan: 1.5)
# #############################################################

def adauga_abonament(s, nume, categorie, cost_lunar, zi_plata):
    a = Abonament(nume=nume, categorie=categorie, cost_lunar=cost_lunar, zi_plata=zi_plata)
    s.add(a)
    s.commit()
    return a

def gaseste_abonament_dupa_nume(s, nume):
    return s.scalar(select(Abonament).where(Abonament.nume == nume))

def toate_abonamentele(s):
    query = select(Abonament).order_by(Abonament.cost_lunar.desc())
    return s.scalars(query).all()

def comuta_abonament(s, abonament_id):
    a = s.get(Abonament, abonament_id)
    if a is None:
        return None
    a.activ = not a.activ
    s.commit()
    return a

def sterge_abonament(s, abonament_id):
    a = s.get(Abonament, abonament_id)
    if a is None:
        return False
    s.delete(a)
    s.commit()
    return True


# #############################################################
# PARTEA 4 - SOLDUL LUNII  (plan: 1.6)
# #############################################################

def sold_luna(s, luna):
    tranzactii = toate_tranzactiile(s, luna=luna)

    venituri = 0
    cheltuieli = 0
    for t in tranzactii:
        if t.tip == "venit":
            venituri = venituri + t.suma
        elif t.tip == "cheltuiala":
            cheltuieli = cheltuieli + t.suma

    abonamente = 0
    for a in toate_abonamentele(s):
        if a.activ:
            abonamente = abonamente + a.cost_lunar

    return {
        "luna": luna,
        "venituri": round(venituri, 2),
        "cheltuieli": round(cheltuieli, 2),
        "abonamente": round(abonamente, 2),
        "sold": round(venituri - cheltuieli - abonamente, 2),
    }

# #############################################################
# PARTEA 5 - get_db()  (plan: 1.7)
# #############################################################

def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
