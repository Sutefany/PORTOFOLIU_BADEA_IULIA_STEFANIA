# =============================================================
# AGENTUL  -  Profesorul de finante personale  (LangChain + RAG)
# =============================================================

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

import s50_rag
from session28.date import OPEN_API_KEY

# #############################################################
# PARTEA 1 - TOOL-UL DE CAUTARE  (plan: 4.1)
# #############################################################

@tool
def cauta_in_lectii(intrebare: str) -> str:
    """Cauta in lectiile de educatie financiara lectiile relevante pentru
    intrebare. Foloseste-l pentru ORICE intrebare despre bani: buget,
    economii, fond de urgenta, dobanda, inflatie, credite, carduri,
    investitii, pensii."""
    rezultate = s50_rag.cauta(intrebare)
    bucati = []
    for r in rezultate:
        bucati.append(f"[{r['titlu']}]\n{r['text']}")
    return "\n\n".join(bucati)

@tool
def calculeaza_dobanda_compusa(suma: float, procent: float, ani: int) -> str:
    """Cauta in lectiile de educatie financiara lectiile relevante pentru
    intrebare. Utilizatorul iti va da o suma initiala, un procent si numarul de ani. Suma pe care o returnezi
    va avea exact 2 zecimale"""
    rezultat = suma * (1 + procent / 100) ** ani
    return (f"Suma este: {rezultat:.2f} -> "
            f"Formula utilizata: suma * (1 + procent / 100) ** ani")

# #############################################################
# PARTEA 2 - AGENTUL
# #############################################################

SYSTEM_PROMPT = (
    "Esti un profesor de educatie financiara pentru adulti. Pentru orice "
    "intrebare despre bani folosesti tool-ul cauta_in_lectii si raspunzi DOAR "
    "pe baza lectiilor gasite. Explici clar, cu exemple simple, si aplici "
    "ideile pe situatia utilizatorului. La final spui din ce lectii ai luat "
    "informatia (titlurile dintre parantezele drepte). Daca lectiile nu acopera "
    "subiectul, spui clar asta - nu inventa. NU recomanzi actiuni, fonduri, "
    "banci sau produse concrete si NU promiti castiguri: spui ca pentru decizii "
    "personale e nevoie de un consultant financiar autorizat. Raspunzi scurt, in romana."
)

llm = ChatOpenAI(model="gpt-4.1-mini", api_key=OPEN_API_KEY)

agent = create_agent(
    llm,
    tools=[cauta_in_lectii, calculeaza_dobanda_compusa],
    system_prompt=SYSTEM_PROMPT
)

# #############################################################
# PARTEA 3 - ruleaza_agent  (plan: 4.2)
# #############################################################

def ruleaza_agent(mesaj: str, istoric: list[dict]):
    messages = istoric + [{"role": "user", "content": mesaj}]
    rezultat = agent.invoke({"messages": messages})
    apeluri = []
    for m in rezultat["messages"]:
        if type(m).__name__ == "ToolMessage":
            apeluri.append({"tool": m.name, "rezultat": m.content})
    raspuns = rezultat["messages"][-1].content
    return raspuns, apeluri
















