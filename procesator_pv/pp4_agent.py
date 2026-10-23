
############################### Asistentul Procesator Procese Verbale (OpenAI) ###############################

### IMPORTURI NECESARE

import json

from openai import OpenAI
from pydantic import ValidationError

import pp1_model
from pp2_schema import PvIn
from configurare_db import api_key

# ###################################################################################
# PARTEA 4A - DATE DESPRE AI
# ###################################################################################

# TODO 4a: alegerea modelului si AI-ului + preluare cheie api de pe platforma aferenta AI-ului

client = OpenAI(api_key=api_key)
MODEL = "gpt-4.1-mini"
MAX_PASI = 5

# ###################################################################################
# PARTEA 4A - SCHEMA TOOL-URILOR (ce "vede" modelul)
# ###################################################################################

# Modelul vede DOAR numele, descrierea si parametrii - descrierea e instructiunea lui.

# TODO 4b: realizarea tool-urilor ajutatoare pentru accesarea functiilor

tools = [
    {
        "type": "function",
        "function": {
            "name": "lista_pv",
            "description": (
                "Returneaza toate procesele verbale din Procesator Procese Verbale (id, echipa, cod, descriere, valori, data)."
                "Regula: afiseaza pe fiecare rand exact pe modelul acesta: ID. ECHIPA => COD - DESCRIERE => VALORI (DATA), unde ID este id-ul unic al fiecarui"
                "rand dat de tool-ul lista_pv. Nu inventa ID-ul! Exemplu: 1. Mara- Olt => COP2 - REFACERI PAVAJE LA STRAZI (TOATE MATERIALELE, TRANSPORTURILE SI MANOPERA INCLUSE) => 10.00 (2026-10-07)"
                "Foloseste informatiile preluate pentru a adauga, sterge sau modifica un proces verbal sau un rand din acesta. "
                "Pentru adaugare vei prelua echipa, codul, valorile si data. Pentru stergerea unui proces verbal intreg vei prelua echipa,"
                " data. Pentru stergerea unui element vei prelua id-ul. Pentru modificare sa preiei id-ul, echipa, codul, data si valoarea elementului."
                            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "echipa": {
                        "type": ["string", "null"],
                        "description": "Filtrul echipa sau null dacă nu se aplică",
                    },
                    "cod": {
                        "type": ["string", "null"],
                        "description": "Filtrul codul sau null dacă nu se aplică",
                    },
                    "data": {
                        "type": ["string", "null"],
                        "description": "Filtrul data sau null dacă nu se aplică",
                    },
                },
                "required": [
                    "echipa",
                    "cod",
                    "data",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_proces_verbal",
            "description": (
                "Adauga un element nou in Procesator Procese Verbale."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "echipa": {
                        "type": "string",
                        "description": (
                            "Format acceptat strict Nume- Judet (ex: Aurel: Prahova)"
                            "Judetele sunt exclusiv din Romania"
                        ),
                    },
                    "cod": {
                        "type": "string",
                        "enum": [
                            "COP1", "COP2", "COP3", "COP4", "COP5",
                            "COP6", "COP8", "COP9", "COP10", "COP11",
                            "COP12", "COP13", "COP14", "COP15", "COP16",
                            "COP17", "COP18", "COP20", "COP21", "COP23",
                            "COP24", "COP26", "COP27", "COP28", "COP29",
                        ],
                    },
                    "valori": {
                        "type": "number",
                        "description": (
                            "Date de tip float (ex: 20.5) fara unitate de masura"
                        ),
                    },
                    "data": {
                        "type": "string",
                        "description": (
                            "Data scrisa pe formatul 2026-12-30, adica AAAA-LL-ZZ"
                        ),
                    },
                },
                "required": [
                    "echipa",
                    "cod",
                    "valori",
                    "data",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sterge_proces_verbal",
            "description": (
                "Sterge definitiv un proces verbal intreg, dupa echipa si data. Mai bine spus, vei sterge toate elementele"
                "ale echipei cerute din data ceruta de utilizator. Doar cand userul cere explicit stergerea!"
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "echipa": {
                        "type": "string",
                    },
                    "data": {
                        "type": "string",
                    },
                },
                "required": [
                    "echipa",
                    "data",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sterge_id",
            "description": (
                "Sterge definitiv un element dupa ID. Mai bine spus, vei sterge un singur element care are ID-ul"
                "cerut de utilizator. Doar cand userul cere explicit stergerea!"
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "pv_id": {
                        "type": "number",
                    },
                },
                "required": ["pv_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "modifica_proces_verbal",
            "description": (
                "Modifica datele dintr-un element al procesului verbal. Utilizatorul va oferi un id, tu il vei cauta"
                "si poate da echipa, codul, data, valoarea. Tu vei modifica elementul conform datelor introduse."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "pv_id": {
                        "type": "integer",
                    },
                    "echipa_noua": {
                        "type": "string",
                        "description": (
                            "Format acceptat strict Nume- Judet (ex: Aurel: Prahova)"
                            "Judetele sunt exclusiv din Romania"
                        ),
                    },
                    "cod_nou": {
                        "type": "string",
                        "enum": [
                            "COP1", "COP2", "COP3", "COP4", "COP5",
                            "COP6", "COP8", "COP9", "COP10", "COP11",
                            "COP12", "COP13", "COP14", "COP15", "COP16",
                            "COP17", "COP18", "COP20", "COP21", "COP23",
                            "COP24", "COP26", "COP27", "COP28", "COP29",
                        ],
                    },
                    "valoare_noua": {
                        "type": ["number", "null"],
                        "description": (
                            "Date de tip float (ex: 20.5) fara unitate de masura. Daca e null, "
                            "nu se tine cont de el, valoarea ramane cum era"
                        ),
                    },
                    "data_noua": {
                        "type": "string",
                        "description": (
                            "Data scrisa pe formatul 2026-12-30, adica AAAA-LL-ZZ"
                        ),
                    },
                },
                "required": [
                    "pv_id",
                    "echipa_noua",
                    "cod_nou",
                    "valoare_noua",
                    "data_noua",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "total_km_echipa_zi",
            "description": (
                "Returneaza suma tuturor valorilor elementelor introduse in care codul apartine listei "
                "['COP11', 'COP13', 'COP20', 'COP27', 'COP28', 'COP29']."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "echipa": {
                        "type": "string",
                        "description": (
                            "Format acceptat strict Nume- Judet (ex: Aurel: Prahova)"
                            "Judetele sunt exclusiv din Romania"
                        ),
                    },
                    "data": {
                        "type": "string",
                        "description": (
                            "Data scrisa pe formatul 2026-12-30, adica AAAA-LL-ZZ"
                        ),
                    },
                },
                "required": [
                    "echipa",
                    "data",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "total_cod",
            "description": (
                "Returneaza suma tuturor valorilor elementelor echipei, datei si codului alese de utilizator."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "echipa": {
                        "type": "string",
                        "description": (
                            "Format acceptat strict Nume- Judet (ex: Aurel: Prahova)"
                            "Judetele sunt exclusiv din Romania"
                        ),
                    },
                    "cod": {
                        "type": "string",
                        "enum": [
                            "COP1", "COP2", "COP3", "COP4", "COP5",
                            "COP6", "COP8", "COP9", "COP10", "COP11",
                            "COP12", "COP13", "COP14", "COP15", "COP16",
                            "COP17", "COP18", "COP20", "COP21", "COP23",
                            "COP24", "COP26", "COP27", "COP28", "COP29",
                        ],
                    },
                    "data": {
                        "type": "string",
                        "description": (
                            "Data scrisa pe formatul 2026-12-30, adica AAAA-LL-ZZ"
                        ),
                    },
                },
                "required": [
                    "echipa",
                    "cod",
                    "data",
                ],
                "additionalProperties": False,
            },
        },
    },
]

# ###################################################################################
# PARTEA 4B - IMPLEMENTAREA TOOL-URILOR
# ###################################################################################
# Fiecare tool = un adaptor subtire peste pp1_model.py: primeste `db`
# + argumentele modelului, cheama functia din model, intoarce un STRING.
# Erorile se intorc ca text, nu ca exceptii - modelul le citeste si
# ii explica userului (sau incearca din nou).

# TODO 4c: listeaza_task_uri -> lista_pv, rezultat ca JSON

def lista_pv(db, echipa, cod, data):
    procese_verbale = pp1_model.toate_pv(db, echipa, cod, data) # toata lista filtrata sau nu
    if not procese_verbale:
        return "Nu exista niciun proces verbal"
    rezultat = []
    for pv in procese_verbale:
        rezultat.append({
            "id": pv.id,
            "echipa": pv.echipa,
            "cod": pv.cod,
            "descriere": pv.descriere,
            "valori": pv.valori,
            "data": pv.data.isoformat()
        })
    return json.dumps(rezultat, ensure_ascii=False)

# TODO 4d: adauga_proces_verbal -> rezultat ca JSON
#  Validarea tuturor datelor introduse exact ca la /post

def adauga_proces_verbal(db, echipa, cod, valori, data):
    try:
        data = PvIn.model_validate({"echipa": echipa, "cod": cod,  "valori": valori, "data": data})
    except ValidationError as e:
        erori = "; ".join(f"{er['loc'][0]}: {er['msg']}" for er in e.errors())
        return f"Eroare de validare: {erori}"
    pv = pp1_model.adauga_pv(db, data.echipa, data.cod, data.valori, data.data)
    pv_nou = {
        "id": pv.id,
        "echipa": pv.echipa,
        "cod": pv.cod,
        "descriere": pv.descriere,
        "valori": pv.valori,
        "data": pv.data.isoformat()
    }
    return f"Element nou adaugat: {json.dumps(pv_nou, ensure_ascii=False)}"

# TODO 4e: sterge_proces_verbal

def sterge_proces_verbal(db, echipa, data):
    pv_sters = pp1_model.sterge_pv(db, echipa, data) # True- exista si s-a sters, False - nu exista
    if not pv_sters:
        return f"Eroare: nu exista procesul verbal al echipei {echipa} din data de {data}"
    return f"Procesul Verbal a fost sters cu succes!"

# TODO 4f: sterge_id

def sterge_id(db, pv_id):
    pv_sters = pp1_model.sterge_dupa_id(db, pv_id)
    if not pv_sters:
        return f"Eroare: nu exista procesul verbal cu id-ul {pv_id}"
    return f"Id task sters: {pv_id}"

# TODO 4g: modifica_proces_verbal
#  verificare deoarece datele vin din exterior

def modifica_proces_verbal(db, pv_id, echipa_noua, cod_nou, data_noua, valoare_noua):
    try:
        data = PvIn.model_validate({"echipa": echipa_noua, "cod": cod_nou, "valori": valoare_noua, "data": data_noua})
    except ValidationError as e:
        erori = "; ".join(f"{er['loc'][0]}: {er['msg']}" for er in e.errors())
        return f"Eroare de validare: {erori}"
    pv_modificat = pp1_model.modificare_pv(db, pv_id, data.echipa, data.cod, data.data, data.valori)  # None daca nu exista sau pv-ul modificat dupa salvare
    if pv_modificat is None:
        return f"Eroare: nu exista procesul verbal cu id-ul {pv_id}"
    return f"Element salvat cu succes! ID: {pv_id}"

# TODO 4h: total_km_echipa_zi

def total_km_echipa_zi(db, echipa, data):
    suma = pp1_model.total_km(db, echipa, data)
    return f"Echipa {echipa} a facut {suma}km in data de {data}"

# TODO 4i: total_cod

def total_cod(db, echipa, cod, data):
    suma = pp1_model.total_dupa_cod(db, echipa, cod, data)
    return (f"Raport {echipa} ({data}) - {suma}\n"
            f"Cod: {cod}\n")

# TODO 4j: listarea functiilor

FUNCTII = {
    "lista_pv": lista_pv,
    "adauga_proces_verbal": adauga_proces_verbal,
    "sterge_proces_verbal": sterge_proces_verbal,
    "sterge_id": sterge_id,
    "modifica_proces_verbal": modifica_proces_verbal,
    "total_km_echipa_zi": total_km_echipa_zi,
    "total_cod": total_cod
}

# ###################################################################################
# PARTEA 4C - BUCLA AGENTICA
# ###################################################################################

#   - istoricul vine din afara (Streamlit -> FastAPI), ca asistentul sa tina minte istoricul conversatiei
#   - for pas in range(MAX_PASI) in loc de while True (fiecare pas e o cerere platita - o limita ce protejeaza)
#   - tool-urile apelate vor fi intoarse pentru testare

# TODO 4k: SYSTEM- definirea rolului si comportamentului AI-ului

SYSTEM = (
    "Esti asistentul aplicatiei Procesator Procese Verbale - un board de procese verbale ale unei firme de telecomunicatii,"
    "fiecare cu echipa, cod, descriere, valori si data."
    "Ajuti userul sa vada, adauge, modifice si sa stearga un element sau un intreg proces verbal, folosind tool-urile disponibile. "
    "Nu inventa ID-uri - daca nu stii ID-ul, listeaza intai procesele verbaale. Raspunzi scurt, in romana."
)

# TODO 4l: ruleaza_agent(db, mesaj, istoric)

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




