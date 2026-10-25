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
# PARTEA 1 - MODELUL: Fisa  (plan: 1.2)
# #############################################################

class Fisa(Base):
    __tablename__ = "s50_fisa"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titlu: Mapped[str] = mapped_column(String(200), unique=True)
    categorie: Mapped[str] = mapped_column(String(30))
    continut: Mapped[str] = mapped_column(Text)
    data: Mapped[date]

    def __str__(self):
        return f"Fisa #{self.id}: {self.titlu} ({self.categorie}, {len(self.continut)} caractere)"

# #############################################################
# PARTEA 1b - PORNIREA BAZEI DE DATE  (plan: 1.3)
# #############################################################

def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

FOLDER_FISE_INITIALE = "fise_initiale"

CATEGORIE_PE_FISIER = {
    "pfa_sau_srl.txt":             "Forme juridice",
    "pfa_impozitare.txt":          "Taxe",
    "srl_microintreprindere.txt":  "Taxe",
    "tva_freelanceri.txt":         "Taxe",
    "facturare.txt":               "Facturare",
    "contract_servicii.txt":       "Clienti si contracte",
    "clienti_din_strainatate.txt": "Clienti si contracte",
    "tarif_freelancer.txt":        "Freelancing",
}

def adauga_date_initiale(s):
    if s.scalars(select(Fisa)).all():
        return

    for nume_fisier in sorted(os.listdir(FOLDER_FISE_INITIALE)):
        cale = os.path.join(FOLDER_FISE_INITIALE, nume_fisier)
        with open(cale, encoding="utf-8") as f:
            text = f.read()

        prima_linie, rest = text.split("\n", 1)
        categorie = CATEGORIE_PE_FISIER.get(nume_fisier, "Altele")
        s.add(Fisa(titlu=prima_linie.strip(), categorie=categorie,
                     continut=rest.strip(), data=date.today()))
    s.commit()

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)

# #############################################################
# PARTEA 2 - CRUD Fisa  (plan: 1.4)
# #############################################################

def adauga_fisa(s, titlu, categorie, continut):
    l = Fisa(titlu=titlu, categorie=categorie, continut=continut, data=date.today())
    s.add(l)
    s.commit()
    return l

def toate_fisele(s, categorie=None):
    query = select(Fisa)
    if categorie:
        query = query.where(Fisa.categorie == categorie)
    query = query.order_by(Fisa.titlu)
    return s.scalars(query).all()

def gaseste_fisa_dupa_titlu(s, titlu):
    return s.scalar(select(Fisa).where(Fisa.titlu == titlu))

def sterge_fisa(s, fisa_id):
    l = s.get(Fisa, fisa_id)
    if l is None:
        return False
    s.delete(l)
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