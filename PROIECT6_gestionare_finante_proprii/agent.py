# =============================================================
# AGENTUL  -  Consilierul financiar AI  (OpenAI)
# =============================================================

import json
from datetime import date

from openai import OpenAI
from pydantic import ValidationError

import model
from schema import AbonamentIn, TranzactieIn
from session28.date import OPEN_API_KEY


api_key = OPEN_API_KEY
client = OpenAI(api_key=api_key)
MODEL = "gpt-4.1-mini"
MAX_PASI = 6

# #############################################################
# PARTEA 1 - SCHEMA TOOL-URILOR
# #############################################################

CATEGORII_TRANZACTIE = ["salariu", "freelance", "alt venit", "mancare", "locuinta",
                        "transport", "facturi", "distractie", "sanatate", "altele"]
CATEGORII_ABONAMENT = ["Streaming", "Muzica", "Sport", "Software", "Telefon & Internet", "Altele"]


tools = [
    {
        "type": "function",
        "function": {
            "name": "listeaza_tranzactii",
            "description": "Returneaza tranzactiile (venituri si cheltuieli), optional filtrate. "
                           "Foloseste-l pentru intrebari de tipul 'cat am cheltuit pe X' sau ca sa afli "
                           "ID-ul unei tranzactii inainte s-o stergi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "luna": {"type": "string", "description": "Luna, format YYYY-MM"},
                    "tip": {"type": "string", "enum": ["venit", "cheltuiala"]},
                    "categorie": {"type": "string", "enum": CATEGORII_TRANZACTIE},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_tranzactie",
            "description": "Inregistreaza o tranzactie facuta O SINGURA DATA: un venit (salariu, "
                           "freelance) sau o cheltuiala (mancare, chirie, factura). NU pentru abonamente lunare.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "descriere": {"type": "string", "description": "Scurt, ex: 'Pizza', 'Salariu'"},
                    "tip": {"type": "string", "enum": ["venit", "cheltuiala"]},
                    "categorie": {"type": "string", "enum": CATEGORII_TRANZACTIE},
                    "suma": {"type": "number", "description": "Suma in lei, mai mare ca 0"},
                    "data": {"type": ["string", "null"],
                             "description": "Data, format YYYY-MM-DD, sau null pentru azi"},
                },
                "required": ["descriere", "tip", "categorie", "suma", "data"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sterge_tranzactie",
            "description": "Sterge o tranzactie, dupa ID. Doar cand userul cere explicit.",
            "parameters": {
                "type": "object",
                "properties": {"tranzactie_id": {"type": "integer"}},
                "required": ["tranzactie_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listeaza_abonamente",
            "description": "Returneaza toate abonamentele (id, nume, categorie, cost_lunar, zi_plata, activ), "
                           "de la cel mai scump la cel mai ieftin.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adauga_abonament",
            "description": "Adauga un abonament nou, platit lunar (Netflix, sala, telefon).",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "nume": {"type": "string"},
                    "categorie": {"type": "string", "enum": CATEGORII_ABONAMENT},
                    "cost_lunar": {"type": "number", "description": "Cost pe luna, in lei"},
                    "zi_plata": {"type": "integer", "description": "Ziua din luna in care se plateste, 1-31"},
                },
                "required": ["nume", "categorie", "cost_lunar", "zi_plata"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "comuta_abonament",
            "description": "Pune pe pauza un abonament activ, sau reactiveaza unul pus pe pauza, dupa ID. "
                           "Foloseste-l cand userul zice ca a renuntat la un abonament (sau ca s-a reabonat).",
            "parameters": {
                "type": "object",
                "properties": {"abonament_id": {"type": "integer"}},
                "required": ["abonament_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sold_luna",
            "description": "Returneaza, pentru o luna: venituri, cheltuieli, abonamente active si "
                           "soldul (venituri - cheltuieli - abonamente).",
            "parameters": {
                "type": "object",
                "properties": {"luna": {"type": "string", "description": "Luna, format YYYY-MM. Implicit luna curenta."}},
                "required": [],
            },
        },
    },
]


# #############################################################
# PARTEA 2 - IMPLEMENTAREA TOOL-URILOR
# #############################################################

def tranzactie_dict(t):
    return {"id": t.id, "descriere": t.descriere, "tip": t.tip, "categorie": t.categorie,
            "suma": t.suma, "data": t.data.isoformat()}


def abonament_dict(a):
    return {"id": a.id, "nume": a.nume, "categorie": a.categorie,
            "cost_lunar": a.cost_lunar, "zi_plata": a.zi_plata, "activ": a.activ}


def erori_validare(e: ValidationError) -> str:
    return "Eroare de validare: " + "; ".join(f"{er['loc'][0]}: {er['msg']}" for er in e.errors())

def listeaza_tranzactii(db, luna=None, tip=None, categorie=None):
    try:
        tranzactii = model.toate_tranzactiile(db, luna, tip, categorie)
    except ValueError:
        return f"Eroare: luna '{luna}' nu e in formatul YYYY-MM."
    if not tranzactii:
        return "Nu exista nicio tranzactie care sa corespunda."

    lista = []
    total = 0
    for t in tranzactii:
        lista.append(tranzactie_dict(t))
        total = total + t.suma

    return json.dumps({"tranzactii": lista, "total": round(total, 2)}, ensure_ascii=False)

def adauga_tranzactie(db, descriere, tip, categorie, suma, data):
    date_brute = {"descriere": descriere, "tip": tip, "categorie": categorie, "suma": suma}
    if data is not None:
        date_brute["data"] = data
    try:
        tr = TranzactieIn.model_validate(date_brute)
    except ValidationError as e:
        return erori_validare(e)

    t = model.adauga_tranzactie(db, tr.descriere, tr.tip.value, tr.categorie.value, tr.suma, tr.data)
    return f"Tranzactie adaugata: {json.dumps(tranzactie_dict(t), ensure_ascii=False)}"

def sterge_tranzactie(db, tranzactie_id):
    if not model.sterge_tranzactie(db, int(tranzactie_id)):
        return f"Eroare: tranzactia {tranzactie_id} nu exista."
    return f"Tranzactia {tranzactie_id} a fost stearsa."

def listeaza_abonamente(db):
    abonamente = model.toate_abonamentele(db)
    if not abonamente:
        return "Nu exista niciun abonament."

    lista = []
    total_activ = 0
    for a in abonamente:
        lista.append(abonament_dict(a))
        if a.activ:
            total_activ += a.cost_lunar
    return json.dumps({'abonamente': lista, 'total_lunar_active': round(total_activ,2)}, ensure_ascii=False)

def adauga_abonament(db, nume, categorie, cost_lunar, zi_plata):
    try:
        ab = AbonamentIn.model_validate({"nume": nume, 'categorie': categorie, 'cost_lunar': cost_lunar, 'zi_plata': zi_plata})
    except ValidationError as e:
        return erori_validare(e)

    if model.gaseste_abonament_dupa_nume(db, ab.nume) is not None:
        return f"Eroare: abonamentul '{ab.nume}' exista deja"

    a = model.adauga_abonament(db, nume, categorie, cost_lunar, zi_plata)
    return f"Abonament adaugat: {json.dumps(abonament_dict(a), ensure_ascii=False)}"

def comuta_abonament(db, abonament_id):
    a = model.comuta_abonament(db, int(abonament_id))
    if a is None:
        return f"Eroare: abonamentul {abonament_id} nu exista."

    if a.activ:
        stare = 'Activ'
    else:
        stare = "Pus pe pauza"

    return f"Abonament {a.nume} e acum {stare}"

def sold_luna(db, luna=None):
    if luna is None:
        luna = model.luna_curenta()

    try:
        return json.dumps(model.sold_luna(db, luna), ensure_ascii=False)
    except ValueError:
        return f"Eroare: luna {luna} nu e in formatul YYYY-MM."


FUNCTII = {
    "listeaza_tranzactii": listeaza_tranzactii,
    "adauga_tranzactie": adauga_tranzactie,
    "sterge_tranzactie": sterge_tranzactie,
    "listeaza_abonamente": listeaza_abonamente,
    "adauga_abonament": adauga_abonament,
    "comuta_abonament": comuta_abonament,
    "sold_luna": sold_luna,
}


# #############################################################
# PARTEA 3 - BUCLA AGENTICA (identica cu s44)
# #############################################################

def system_prompt():
    return (
        "Esti consilierul financiar al aplicatiei 'Bugetul meu'. Ajuti userul "
        "sa isi inregistreze veniturile, cheltuielile si abonamentele, si sa "
        "le inteleaga, folosind tool-urile disponibile. "
        "O plata facuta o data e o TRANZACTIE; o plata care se repeta lunar e "
        "un ABONAMENT. Nu inventa ID-uri si nu aduna sume din cap - foloseste "
        "totalurile intoarse de tool-uri. Cand userul cere sfaturi de economisire, "
        "uita-te la date si da 2-3 sugestii concrete (ex: abonamente scumpe sau "
        "din aceeasi categorie). Nu recomanda investitii concrete si nu promite "
        "randamente - spune ca pentru asta e nevoie de un consultant autorizat. "
        f"Data de azi este {date.today().isoformat()}. "
        "Raspunzi scurt, in romana, cu sumele in lei."
    )


def ruleaza_agent(db, mesaj: str, istoric: list[dict]):
    messages = [{"role": "system", "content": system_prompt()}]
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


