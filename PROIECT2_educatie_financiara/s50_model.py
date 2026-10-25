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
# PARTEA 1 - MODELUL: Lectie  (plan: 1.2)
# #############################################################

class Lectie(Base):
    __tablename__ = "s50_lectie"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titlu: Mapped[str] = mapped_column(String(200), unique=True)
    categorie: Mapped[str] = mapped_column(String(30))
    continut: Mapped[str] = mapped_column(Text)
    data: Mapped[date]

    def __str__(self):
        return f"Lectie #{self.id}: {self.titlu} ({self.categorie}, {len(self.continut)} caractere)"

# #############################################################
# PARTEA 1b - PORNIREA BAZEI DE DATE  (plan: 1.3)
# #############################################################

def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

FOLDER_LECTII_INITIALE = "lectii_initiale"

CATEGORIE_PE_FISIER = {
    "buget_personal.txt":   "Buget",
    "fond_de_urgenta.txt":  "Economii",
    "dobanda_compusa.txt":  "Economii",
    "inflatia.txt":         "Economii",
    "credite_dae.txt":      "Credite",
    "card_de_credit.txt":   "Credite",
    "investitii_etf.txt":   "Investitii",
    "pensii_piloni.txt":    "Pensie",
}

def adauga_date_initiale(s):
    if s.scalars(select(Lectie)).all():
        return

    for nume_fisier in sorted(os.listdir(FOLDER_LECTII_INITIALE)):
        cale = os.path.join(FOLDER_LECTII_INITIALE, nume_fisier)
        with open(cale, encoding="utf-8") as f:
            text = f.read()

        prima_linie, rest = text.split("\n", 1)
        categorie = CATEGORIE_PE_FISIER.get(nume_fisier, "Altele")
        s.add(Lectie(titlu=prima_linie.strip(), categorie=categorie,
                     continut=rest.strip(), data=date.today()))
    s.commit()

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)

# #############################################################
# PARTEA 2 - CRUD Lectie  (plan: 1.4)
# #############################################################

def adauga_lectie(s, titlu, categorie, continut):
    l = Lectie(titlu=titlu, categorie=categorie, continut=continut, data=date.today())
    s.add(l)
    s.commit()
    return l

def toate_lectiile(s, categorie=None):
    query = select(Lectie)
    if categorie:
        query = query.where(Lectie.categorie == categorie)
    query = query.order_by(Lectie.titlu)
    return s.scalars(query).all()

def gaseste_lectie_dupa_titlu(s, titlu):
    return s.scalar(select(Lectie).where(Lectie.titlu == titlu))

def sterge_lectie(s, lectie_id):
    l = s.get(Lectie, lectie_id)
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

