
############################### VALIDARE CU PYDANTIC ###############################

# Validarea datelor ce vor veni din exterior: din Streamlit sau de la Agentul AI
# Daca datele nu sunt respectate, Pydantic arunca ValidationError si datele gresite nu vor mai fi salvate in baza de date

### IMPORTURI NECESARE

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, ValidationError # eroare de validare pentru testare

# ###################################################################################
# PARTEA 2A - ProceseVerbale - validarea datelor
# ###################################################################################

# TODO 2a: clasa Cod_Permis(str, Enum) - categoriile permise
#   Membrii (NUME = "valoare"):
#       COP1      = "COP1"
#       .................
#       COP29     = "COP29"

class Cod_Permis(str, Enum):
    COP1      = "COP1"
    COP2      = "COP2"
    COP3      = "COP3"
    COP4      = "COP4"
    COP5      = "COP5"
    COP6      = "COP6"
    COP8      = "COP8"
    COP9      = "COP9"
    COP10     = "COP10"
    COP11     = "COP11"
    COP12     = "COP12"
    COP13     = "COP13"
    COP14     = "COP14"
    COP15     = "COP15"
    COP16     = "COP16"
    COP17     = "COP17"
    COP18     = "COP18"
    COP20     = "COP20"
    COP21     = "COP21"
    COP23     = "COP23"
    COP24     = "COP24"
    COP26     = "COP26"
    COP27     = "COP27"
    COP28     = "COP28"
    COP29     = "COP29"

# TODO 2b: clasa PvIn(BaseModel) - date noi primite de la client sau de la agent.
#   Nu are id - id-ul il pune MySQL la salvare.
#   exemplu model echipa: in Streamlit se va completa cu numele (ex:"      marian      ") si cu judetul cu selectbox (ex:"Arges")
#                          echipa = "      marian     -Arges" => trebuie sa fie scrisa astfel: "Marian- Arges"
#   descrierea lipseste deoarece este luata automat din Sablon => nu exista greseli daca in Sablon este totul corect

#   camp        tip                    regula (cu Field)
#   echipa      str                    min_length=5, max_length=50
#                                      + VALIDARE BEFORE -> Angajat- Judet (@fieldvalidator si @classmethod)
#                                      + in Streamlit se va completa numele separat de judet (ce va fi selectbox pt a evita greselile de scriere)
#                                      + se va face o lista cu judetele din Romania
#                                      -> daca [Nume, Judet] identifica Judetul incorect -> ValueError (pentru AI mai mult)
#   cod         Cod                    (enum-ul de mai sus, fara Field)
#   valori      float                  gt = 0 (strict mai mare ca 0)
#   data        date                   default_factory=date.today
#                                      (daca lipseste -> data de azi)

judete_permise = ["Alba", "Arad", "Arges", "Bacau", "Bihor", "Bistrita", "Botosani", "Braila", "Brasov",
                  "Buzau", "Calarasi", "Cluj", "Constanta", "Covasna", "Dambovita", "Dolj", "Galati",
                  "Giurgiu", "Gorj", "Harghita", "Hunedoara", "Ialomita", "Iasi", "Ilfov", "Maramures", "Mehedinti",
                  "Mures", "Neamt", "Olt", "Prahova", "Salaj", "Satu Mare", "Severin", "Sibiu", "Suceava", "Teleorman",
                  "Timis", "Tulcea", "Valcea", "Vaslui", "Vrancea", "Bucuresti"]

class PvIn(BaseModel):
    echipa: str = Field(min_length=5, max_length=50)
    cod: Cod_Permis
    valori: float = Field(gt=0)
    data: date = Field(default_factory=date.today)

    @field_validator("echipa", mode='before')
    @classmethod
    def norm_echipa(cls, echipa: str) -> str:
        lista_nume_judet = echipa.split("-") # primul element este numele, al doilea este Judetul
        if len(lista_nume_judet) != 2:
            raise ValueError("Format necesar: Angajat- JudetPermis")
        angajat = lista_nume_judet[0].strip().title()
        judet = lista_nume_judet[1].strip().title()
        if judet not in judete_permise:
            raise ValueError(f"{judet} nu este JUDET PERMIS!")
        return f"{angajat}- {judet}"

# TESTARE VALIDARE
# try:
#     pv = PvIn(echipa="      marian     -Arges", cod="COP2", valori=23.6, data=date(2020, 1, 1))
#     print(pv.echipa)   # Marian- Arges => OK
# except ValidationError as e:
#     print(f"Nr. ERORI: {len(e.errors())}")
#     for eroare in e.errors():
#         print(f"DETALII: {eroare['msg']}")
# print()
# try:
#     pv = PvIn(echipa="      marian     -Arges", cod="COP50", valori=0, data=date(2020, 1, 1))
#     print(pv.echipa)   # NU EXISTA CODUL, VALOARE <= 0
# except ValidationError as e:
#     print(f"Nr. ERORI: {len(e.errors())}")
#     for eroare in e.errors():
#         print(f"DETALII: {eroare['msg']}")
# print()
# try:
#     pv = PvIn(echipa="      marian     -Pisica", cod="COP50", valori=-10, data="2026")
#     print(pv.echipa)   # Pisica nu este JUDET!
# except ValidationError as e:
#     print(f"Nr. ERORI: {len(e.errors())}")
#     for eroare in e.errors():
#         print(f"DETALII: {eroare['msg']}")

# #############################################################
# PARTEA 2B - CHAT CU AGENTUL
# #############################################################
# Ce primeste si ce intoarce POST /chat. Serverul NU tine minte conversatia - Streamlit trimite de fiecare data tot istoricul.
# Un exemplu de cerere (ChatIn) si de raspuns (ChatOut):
#   cerere:   {"mesaj": "Sterge pv-ul cu datele <...>",
#              "istoric": [{"role": "user", "content": "Salut"},
#                          {"role": "assistant", "content": "Salut! Cu ce te ajut?"}]}
#
#   raspuns:  {"raspuns": "Am sters procesul verbal sugerat de tine",
#              "apeluri": [{"tool": "sterge_pv",
#                           "argumente": {"descriere": ...},
#                           "rezultat": "Proces verbal sters: {...}"}]}

# TODO 2c: clasa MesajChat(BaseModel) - UN mesaj din istoric
#   camp      tip
#   role      Literal["user", "assistant"]   - doar unul din aceste doua texte
#   content   str                            - textul mesajului
#
# Literal: fara system (schimbarea comportamentului agentului) -> doar user si assitant

class MesajChat(BaseModel):
    role: Literal["user", "assistant"]
    content: str

# TODO 2d: clasa ChatIn(BaseModel) - ce primeste POST /chat
#   camp      tip                 regula
#   mesaj     str                 Field(min_length=1) - nu poate fi gol
#   istoric   list[MesajChat]     implicit lista goala: = []
#                                 (la primul mesaj nu exista istoric)

class ChatIn(BaseModel):
    mesaj: str = Field(min_length=1)
    istoric: list[MesajChat] = []

# TODO 2e: clasa ApelTool(BaseModel) - UN tool apelat de agent
#   Il trimitem inapoi ca pagina Consilier AI sa arate ce a facut agentul.
#   camp       tip
#   tool       str    - numele tool-ului, ex: "adauga_tranzactie"
#   argumente  dict   - ce argumente a ales modelul, ex: {"suma": 45, ...}
#   rezultat   str    - ce a intors functia tool-ului

class ApelTool(BaseModel):
    tool: str
    argumente: dict
    rezultat: str

# TODO 2f: clasa ChatOut(BaseModel) - ce intoarce POST /chat
#   camp      tip
#   raspuns   str              - textul final al agentului
#   apeluri   list[ApelTool]   - toate tool-urile apelate, in ordine
#                                (lista goala daca nu a apelat niciunul)

class ChatOut(BaseModel):
    raspuns: str
    apeluri: list[ApelTool] = []









