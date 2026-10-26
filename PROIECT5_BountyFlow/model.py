from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from session28.date import username, password

engine = create_engine(f"mysql+pymysql://{username}:{password}@localhost:3306/portofoliu")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# #############################################################
# PARTEA 1 - MODELUL: Task
# #############################################################

class Task(Base):
    __tablename__ = "task-uri"

    id:          Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    titlu:       Mapped[str]   = mapped_column(String(200))
    limbaj:      Mapped[str]   = mapped_column(String(20))
    dificultate: Mapped[str]   = mapped_column(String(10))
    recompensa:  Mapped[float]
    rezolvat:    Mapped[bool]  = mapped_column(default=False)

    def __repr__(self):
        return f"<Task id={self.id} titlu={self.titlu!r} rezolvat={self.rezolvat}>"

class User(Base):
    __tablename__ = "user"

    id:           Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username:     Mapped[str] = mapped_column(String(50), unique=True)
    parola_hash:  Mapped[str] = mapped_column(String(200))

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r}>"


def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

# reset_db()

def adauga_date_initiale(s):
    if not s.scalars(select(Task)).all():
        s.add_all([
            Task(titlu="Fix bug la login",     limbaj="Python",     dificultate="usor",  recompensa=50),
            Task(titlu="Adauga dark mode",      limbaj="JavaScript", dificultate="mediu", recompensa=150),
            Task(titlu="Optimizeaza query SQL", limbaj="Python",     dificultate="greu",  recompensa=300, rezolvat=True),
        ])
        s.commit()

def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        adauga_date_initiale(s)

init_db()

# #############################################################
# PARTEA 2 - CRUD Task (recap)
# #############################################################

def adauga_task(s, titlu, limbaj, dificultate, recompensa):
    t = Task(titlu=titlu, limbaj=limbaj, dificultate=dificultate, recompensa=recompensa)
    s.add(t)
    s.commit()
    return t

def toate_task_urile(s):
    return s.scalars(select(Task).order_by(Task.id)).all()

def un_task(s, task_id):
    return s.get(Task, task_id)

def marcheaza_rezolvat(s, task_id):
    t = s.get(Task, task_id)
    if t is None:
        return None
    t.rezolvat = True
    s.commit()
    return t

def sterge_task(s, task_id):
    t = s.get(Task, task_id)
    if t is None:
        return False
    s.delete(t)
    s.commit()
    return True

def recompensa_disponibila(s):
    nerezolvate = s.scalars(select(Task).where(Task.rezolvat == False)).all()
    return float(sum(t.recompensa for t in nerezolvate))

# #############################################################
# PARTEA 3 - USER: creare si cautare (nou)
# #############################################################

def creeaza_user(s, username, parola_hash):
    u = User(username=username, parola_hash=parola_hash)
    s.add(u)
    s.commit()
    return u

def gaseste_user_dupa_username(s, username):
    return s.scalar(select(User).where(User.username == username))

# #############################################################
# PARTEA 4 - get_db(): dependency pentru FastAPI
# #############################################################

def get_db():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
