# =============================================================
# AGENTUL  -  Asistentul Bounty Board  (OpenAI)
# =============================================================

import json

from openai import OpenAI
from pydantic import ValidationError

import model
from schema import TaskIn
from session28.date import OPEN_API_KEY

client = OpenAI(api_key=OPEN_API_KEY)
MODEL = "gpt-4.1-mini"
MAX_PASI = 5

# #############################################################
# PARTEA 1 - SCHEMA TOOL-URILOR
# #############################################################

tools = [
    {
        "type": "function",
        "function": {
            "name": "listeaza_task_uri",
            "description": "Returneaza toate task-urile din Bounty Board (id, titlu, limbaj, "
                           "dificultate, recompensa, rezolvat). Foloseste-l ca sa afli ID-ul "
                           "unui task inainte sa-l rezolvi sau sa-l stergi.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_task",
            "description": "Adauga un task nou in Bounty Board.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "titlu": {"type": "string", "description": "Titlul task-ului, minim 3 caractere"},
                    "limbaj": {"type": "string", "enum": ["Python", "JavaScript", "Go", "Rust"]},
                    "dificultate": {"type": "string", "enum": ["usor", "mediu", "greu"]},
                    "recompensa": {"type": "number", "description": "Recompensa in RON, mai mare ca 0"},
                },
                "required": ["titlu", "limbaj", "dificultate", "recompensa"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "marcheaza_rezolvat",
            "description": "Marcheaza un task ca rezolvat, dupa ID.",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sterge_task",
            "description": "Sterge definitiv un task, dupa ID. Doar cand userul cere explicit stergerea.",
            "parameters": {
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recompensa_disponibila",
            "description": "Returneaza suma recompenselor tuturor task-urilor nerezolvate.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# #############################################################
# PARTEA 2 - IMPLEMENTAREA TOOL-URILOR
# #############################################################

def listeaza_task_uri(db):
    task_uri = model.toate_task_urile(db)
    if not task_uri:
        return "Nu exista niciun task."
    rezultat = []
    for t in task_uri:
        rezultat.append({"id": t.id, "titlu": t.titlu, "limbaj": t.limbaj,
                         "dificultate": t.dificultate, "recompensa": t.recompensa,
                         "rezolvat": t.rezolvat})
    return json.dumps(rezultat, ensure_ascii=False)

def adauga_task(db, titlu, limbaj, dificultate, recompensa):
    try:
        data = TaskIn.model_validate({"titlu": titlu, "limbaj": limbaj,
                                      "dificultate": dificultate, "recompensa": recompensa})
    except ValidationError as e:
        erori = "; ".join(f"{er['loc'][0]}: {er['msg']}" for er in e.errors())
        return f"Eroare de validare: {erori}"

    t = model.adauga_task(db, data.titlu, data.limbaj, data.dificultate, data.recompensa)
    task_nou = {"id": t.id, "titlu": t.titlu, "limbaj": t.limbaj,
                "dificultate": t.dificultate, "recompensa": t.recompensa,
                "rezolvat": t.rezolvat}
    return f"Task adaugat: {json.dumps(task_nou, ensure_ascii=False)}"

def marcheaza_rezolvat(db, task_id):
    t = model.marcheaza_rezolvat(db, int(task_id))
    if t is None:
        return f"Eroare: task-ul {task_id} nu exista."
    return f"Task-ul {t.id} ('{t.titlu}') e acum rezolvat."

def sterge_task(db, task_id):
    if not model.sterge_task(db, int(task_id)):
        return f"Eroare: task-ul {task_id} nu exista."
    return f"Task-ul {task_id} a fost sters."

def recompensa_disponibila(db):
    return f"Recompensa disponibila: {model.recompensa_disponibila(db):.0f} RON"

FUNCTII = {
    "listeaza_task_uri": listeaza_task_uri,
    "adauga_task": adauga_task,
    "marcheaza_rezolvat": marcheaza_rezolvat,
    "sterge_task": sterge_task,
    "recompensa_disponibila": recompensa_disponibila,
}

# #############################################################
# PARTEA 3 - BUCLA AGENTICA
# #############################################################

SYSTEM = (
    "Esti asistentul aplicatiei Bounty Board - un board de task-uri de "
    "programare, fiecare cu limbaj, dificultate si o recompensa in RON. "
    "Ajuti userul sa vada, adauge, rezolve si stearga task-uri, folosind "
    "tool-urile disponibile. Nu inventa ID-uri - daca nu stii ID-ul, "
    "listeaza intai task-urile. Raspunzi scurt, in romana."
)


def ruleaza_agent(db, mesaj: str, istoric: list[dict]):
    messages = [{"role": "system", "content": SYSTEM}]
    messages += istoric
    messages.append({"role": "user", "content": mesaj})

    apeluri = []

    for pas in range(MAX_PASI):
        raspuns = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
        mesaj_model = raspuns.choices[0].message

        if not mesaj_model.tool_calls:
            return mesaj_model.content, apeluri

        messages.append(mesaj_model)

        for apel in mesaj_model.tool_calls:
            nume = apel.function.name
            argumente = json.loads(apel.function.arguments)

            functie = FUNCTII.get(nume)
            rezultat = functie(db, **argumente) if functie else f"Eroare: tool necunoscut '{nume}'"

            apeluri.append({"tool": nume, "argumente": argumente, "rezultat": rezultat})
            messages.append({"role": "tool", "tool_call_id": apel.id, "content": rezultat})

    return "Nu am reusit sa termin in numarul maxim de pasi. Incearca o cerere mai simpla.", apeluri


