from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

# #############################################################
# PARTEA 1 - GHID  (plan: 2.1)
# #############################################################

class Categorie(str, Enum):
    CV_PORTOFOLIU = "CV si portofoliu"
    INTERVIU      = "Interviu"
    NEGOCIERE     = "Negociere"
    ROLURI        = "Roluri IT"
    LA_JOB        = "La job"
    ALTELE        = "Altele"

class GhidIn(BaseModel):
    titlu:     str = Field(min_length=3, max_length=200)
    categorie: Categorie
    continut:  str = Field(min_length=50)


# #############################################################
# PARTEA 2 - CHAT CU MENTORUL  (plan: 2.2)
# #############################################################

class MesajChat(BaseModel):
    role:    Literal["user", "assistant"]
    content: str

class ChatIn(BaseModel):
    mesaj:   str = Field(min_length=1)
    istoric: list[MesajChat] = []

class ApelTool(BaseModel):
    tool:     str
    rezultat: str

class ChatOut(BaseModel):
    raspuns: str
    apeluri: list[ApelTool]
