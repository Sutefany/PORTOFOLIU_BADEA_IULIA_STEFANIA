# =============================================================================================
# MINI-PROIECT: "Radar Biziday"  (Web Scraping) - AGENTUL AI - intrebari specifice, categorii
# =============================================================================================

import json
from openai import OpenAI
from date import OPEN_API_KEY

api_key = OPEN_API_KEY
client = OpenAI(api_key=api_key)
MODEL = "gpt-4.1-mini"
MAX_PASI = 6

# #############################################################
# PARTEA 1 - SCHEMA TOOL-ULUI
# #############################################################

CATEGORII_CLASICE = ["sport", "sanatate", "politica", "educatie", "mediu si clima", "economie si finante",
                     "social", "justitie", "stiinta si tehnologie", "energie", "transport", "cultura si divertisment",
                     "diverse"]

EFECT = ["pozitiv", "negativ", "neutru"]

LOCATIE = ["national", "european", "mondial"]

tools = [
    {
        "type": "function",
        "function": {
            "name": "clasifica_stirea",
            "description": (
                "Clasifica textul unei stiri dupa categoria principala, "
                "efectul general si localizarea evenimentului."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "categorie": {
                        "type": "string",
                        "enum": CATEGORII_CLASICE,
                        "description": "Categoria principala a stirii.",
                    },
                    "efect": {
                        "type": "string",
                        "enum": EFECT,
                        "description": (
                            "Efectul general prezentat de stire."
                        ),
                    },
                    "locatie": {
                        "type": "string",
                        "enum": LOCATIE,
                        "description": (
                            "national pentru Romania, european pentru "
                            "Europa si mondial pentru restul lumii "
                            "sau evenimente globale."
                        ),
                    },
                },
                "required": [
                    "categorie",
                    "efect",
                    "locatie",
                ],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]


# #############################################################
# PARTEA 2 - IMPLEMENTAREA TOOL-URILOR
# #############################################################

def clasifica_stirea(categorie, efect, locatie):
    return json.dumps({"categorie": categorie, "efect": efect, "locatie": locatie,},ensure_ascii=False)

FUNCTII = {"clasifica_stirea": clasifica_stirea}

# #############################################################
# PARTEA 3 - BUCLA AGENTICA (identica cu s44)
# #############################################################

def system_prompt():
    return (
        """
    "Esti un filtru de titluri de stiri. Tu vei primi un text, ii vei intelege sensul si il vei categorisi conform unor"
    "liste date (categorie, efect, locatie)"
    "Reguli pentru categorie:"
    "- Alege categoria după subiectul principal al știrii."
    "- Nu clasifica doar după apariția unui cuvânt."
    "- Folosește categoria „diverse” numai dacă nicio altă categorie nu este potrivită."
    "Reguli pentru efect:"
    "- „pozitiv” pentru progres, succes, îmbunătățire sau rezultat favorabil;"
    "- „negativ” pentru accidente, conflicte, pierderi, pericole sau probleme;"
    "- „neutru” pentru informații predominant factuale sau cu efect neclar."
    "Reguli pentru locație:"
    "- „national” dacă subiectul principal privește România;"
    "- „european” dacă privește altă țară europeană sau Uniunea Europeană;"
    "- „mondial” dacă privește exteriorul Europei sau are caracter global."
    "Returnează numai clasificarea cerută de schema primită."
"""
    )

def ruleaza_agent(mesaj: str, istoric: list[dict]):

    messages = [{"role": "system", "content": system_prompt()}]

    messages += istoric

    messages.append({
        "role": "user",
        "content": mesaj})

    raspuns = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "clasifica_stirea"}}
    )

    mesaj_model = raspuns.choices[0].message
    apel = mesaj_model.tool_calls[0]

    argumente = json.loads(apel.function.arguments)
    rezultat = clasifica_stirea(**argumente)

    apeluri = [{
        "tool": apel.function.name,
        "argumente": argumente,
        "rezultat": rezultat}]

    return argumente, apeluri
