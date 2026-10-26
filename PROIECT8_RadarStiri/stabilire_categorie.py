# =============================================================================================
# MINI-PROIECT: "Radar Biziday"  (Web Scraping) - AGENTUL AI - incadrare stiri in categoria data
# =============================================================================================

from enum import Enum
from pydantic import BaseModel

class Categorie(str, Enum):
    SPORT = "sport"
    SANATATE = "sanatate"
    POLITICA = "politica"
    EDUCATIE = "educatie"
    MEDIU = "mediu si clima"
    ECONOMIE = "economie si finante"
    SOCIAL = "social"
    JUSTITIE = "justitie"
    STIINTA_TEHNOLOGIE = "stiinta si tehnologie"
    ENERGIE = "energie"
    TRANSPORT = "transport"
    CULTURA = "cultura si divertisment"
    DIVERSE = "diverse"

class Efect(str, Enum):
    POZITIV = "pozitiv"
    NEGATIV = "negativ"
    NEUTRU = "neutru"

class Locatie(str, Enum):
    NATIONAL = "national"
    EUROPEAN = "european"
    INTERNATIONAL = "mondial"

class ClasificareStire(BaseModel):
    categorie: Categorie
    efect: Efect
    locatie: Locatie
