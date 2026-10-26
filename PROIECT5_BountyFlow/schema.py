from enum import Enum
from pydantic import BaseModel, Field

# #############################################################
# PARTEA 1 - TASK
# #############################################################

class Limbaj(str, Enum):
    PYTHON     = "Python"
    JAVASCRIPT = "JavaScript"
    GO         = "Go"
    RUST       = "Rust"

class Dificultate(str, Enum):
    USOR  = "usor"
    MEDIU = "mediu"
    GREU  = "greu"

class TaskIn(BaseModel):
    titlu:       str = Field(min_length=3)
    limbaj:      Limbaj
    dificultate: Dificultate
    recompensa:  float = Field(gt=0)

# #############################################################
# PARTEA 2 - CHAT CU AGENTUL
# #############################################################

class Rol(str, Enum):
    USER      = "user"
    ASSISTANT = "assistant"

class MesajChat(BaseModel):
    role:    Rol
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

# #############################################################
# PARTEA 2 - AUTENTIFICARE
# #############################################################

class UserIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    parola:   str = Field(min_length=6)

class LoginIn(BaseModel):
    username: str
    parola:   str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"






