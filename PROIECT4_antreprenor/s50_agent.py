# =============================================================
# AGENTUL  -  Asistentul pentru antreprenori  (LangChain + RAG)
# =============================================================

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from session28.date import OPEN_API_KEY
import s50_rag

# #############################################################
# PARTEA 1 - TOOL-UL DE CAUTARE  (plan: 4.1)
# #############################################################

@tool
def cauta_in_fise(intrebare: str) -> str:
    """Cauta in fisele pentru antreprenori fisele relevante pentru
    intrebare. Foloseste-l pentru ORICE intrebare despre lucrul pe cont
    propriu: PFA, SRL, microintreprindere, taxe si contributii, TVA,
    facturare, e-Factura, contracte, clienti din strainatate, tarife."""
    rezultate = s50_rag.cauta(intrebare)
    bucati = []
    for r in rezultate:
        bucati.append(f"[{r['titlu']}]\n{r['text']}")
    return "\n\n".join(bucati)

# #############################################################
# PARTEA 2 - AGENTUL
# #############################################################

SYSTEM_PROMPT = (
    "Esti un asistent pentru persoanele care incep sa lucreze pe cont propriu "
    "(PFA, SRL, freelancing). Pentru orice intrebare folosesti tool-ul "
    "cauta_in_fise si raspunzi DOAR pe baza fiselor gasite. Explici clar, cu "
    "exemple simple, si aplici ideile pe situatia utilizatorului. La final spui "
    "din ce fise ai luat informatia (titlurile dintre parantezele drepte). Daca "
    "fisele nu acopera subiectul, spui clar asta - nu inventa. NU dai cote de "
    "impozitare, plafoane sau termene exacte daca nu apar in fise: regulile "
    "fiscale se schimba des, iar pentru decizii personale recomanzi un contabil "
    "sau un avocat. Raspunzi scurt, in romana."
)

llm = ChatOpenAI(model="gpt-4.1-mini", api_key=OPEN_API_KEY)

agent = create_agent(
    llm,
    tools=[cauta_in_fise],
    system_prompt=SYSTEM_PROMPT,
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