import os
from datetime import date

from sqlalchemy import create_engine, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# #############################################################
# PARTEA 0 - CONEXIUNEA LA MySQL  (plan: 1.1)
# #############################################################

from session28.date import username, password # pentru limitarea vizibilitatii username-ului si parolei

engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost:3306/curs")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# #############################################################
# PARTEA 1 - MODELUL: Ghid  (plan: 1.2)
# #############################################################

class Ghid(Base):
    __tablename__ = "s50_ghid"

    id:        Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    titlu:     Mapped[str]  = mapped_column(String(200), unique=True)
    categorie: Mapped[str]  = mapped_column(String(30))
    continut:  Mapped[str]  = mapped_column(Text)
    data:      Mapped[date]

    def __str__(self):
        return f"Ghid #{self.id}: {self.titlu} ({self.categorie}, {len(self.continut)} caractere)"

# #############################################################
# PARTEA 1b - PORNIREA BAZEI DE DATE  (plan: 1.3)
# #############################################################

def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

FOLDER_GHIDURI_INITIALE = "ghiduri_initiale"

CATEGORIE_PE_FISIER = {
    "cv_primul_job.txt":           "CV si portofoliu",
    "portofoliu_github.txt":       "CV si portofoliu",
    "linkedin_networking.txt":     "CV si portofoliu",
    "interviu_comportamental.txt": "Interviu",
    "interviu_tehnic.txt":         "Interviu",
    "negociere_salariala.txt":     "Negociere",
    "roluri_in_it.txt":            "Roluri IT",
    "primele_90_de_zile.txt":      "La job",
}

def adauga_date_initiale(s):
    if s.scalars(select(Ghid)).all():
        return

    for nume_fisier in sorted(os.listdir(FOLDER_GHIDURI_INITIALE)):
        cale = os.path.join(FOLDER_GHIDURI_INITIALE, nume_fisier)
        with open(cale, encoding="utf-8") as f:
            text = f.read()

        prima_linie, rest = text.split("\n", 1)
        categorie = CATEGORIE_PE_FISIER.get(nume_fisier, "Altele")
        s.add(Ghid(titlu=prima_linie.strip(), categorie=categorie,
                   continut=rest.strip(), data=date.today()))
    s.commit()

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)

# #############################################################
# PARTEA 2 - CRUD Ghid  (plan: 1.4)
# #############################################################

def adauga_ghid(s, titlu, categorie, continut):
    g = Ghid(titlu=titlu, categorie=categorie, continut=continut, data=date.today())
    s.add(g)
    s.commit()
    return g

def toate_ghidurile(s, categorie=None):
    query = select(Ghid)
    if categorie:
        query = query.where(Ghid.categorie == categorie)
    query = query.order_by(Ghid.titlu)
    return s.scalars(query).all()

def gaseste_ghid_dupa_titlu(s, titlu):
    return s.scalar(select(Ghid).where(Ghid.titlu == titlu))

def sterge_ghid(s, ghid_id):
    g = s.get(Ghid, ghid_id)
    if g is None:
        return False
    s.delete(g)
    s.commit()
    return True

# #############################################################
# PARTEA 3 - get_db()
# #############################################################

def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()

### Apelare obligatorie la inceput pentru trecerea documentelor in baza de date

# init_db()