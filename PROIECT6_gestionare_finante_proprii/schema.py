from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# #############################################################
# PARTEA 1 - TRANZACTIE  (plan: 2.1)
# #############################################################

class Tip(str, Enum):
    VENIT      = "venit"
    CHELTUIALA = "cheltuiala"


class CategorieTranzactie(str, Enum):
    # venituri
    SALARIU    = "salariu"
    FREELANCE  = "freelance"
    ALT_VENIT  = "alt venit"
    # cheltuieli
    MANCARE    = "mancare"
    LOCUINTA   = "locuinta"
    TRANSPORT  = "transport"
    FACTURI    = "facturi"
    DISTRACTIE = "distractie"
    SANATATE   = "sanatate"
    ALTELE     = "altele"


class TranzactieIn(BaseModel):
    descriere: str = Field(min_length=2, max_length=200)
    tip:       Tip
    categorie: CategorieTranzactie
    suma:      float = Field(gt=0)
    data:      date = Field(default_factory=date.today)


# #############################################################
# PARTEA 2 - ABONAMENT  (plan: 2.2)
# #############################################################

class CategorieAbonament(str, Enum):
    STREAMING = "Streaming"
    MUZICA    = "Muzica"
    SPORT     = "Sport"
    SOFTWARE  = "Software"
    TELEFON   = "Telefon & Internet"
    ALTELE    = "Altele"

class AbonamentIn(BaseModel):
    nume:       str = Field(min_length=2, max_length=100)
    categorie:  CategorieAbonament
    cost_lunar: float = Field(gt=0)
    zi_plata:   int = Field(ge=1, le=31)


# #############################################################
# PARTEA 3 - CHAT CU AGENTUL  (plan: 2.3)
# #############################################################

class MesajChat(BaseModel):
    role:    Literal["user", "assistant"]
    content: str

class ChatIn(BaseModel):
    mesaj:   str = Field(min_length=1)
    istoric: list[MesajChat] = []

class ApelTool(BaseModel):
    tool:      str
    argumente: dict
    rezultat:  str

class ChatOut(BaseModel):
    raspuns: str
    apeluri: list[ApelTool]
