# =============================================================
# AGENTUL  -  Mentorul de cariera IT  (LangChain + RAG)
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
def cauta_in_ghiduri(intrebare: str) -> str:
    """Cauta in ghidurile de cariera IT ghidurile relevante pentru
    intrebare. Foloseste-l pentru ORICE intrebare despre cariera in IT:
    CV, portofoliu, LinkedIn, interviuri, negocierea salariului, roluri in
    IT, primele luni la un job nou."""
    rezultate = s50_rag.cauta(intrebare)

    bucati = []
    for r in rezultate:
        bucati.append(f"[{r['titlu']}]\n{r['text']}")
    return"\n\n".join(bucati)

# #############################################################
# PARTEA 2 - AGENTUL
# #############################################################

SYSTEM_PROMPT = (
    "Esti un mentor de cariera pentru persoane care se reorienteaza spre IT. "
    "Pentru orice intrebare despre cariera folosesti tool-ul cauta_in_ghiduri "
    "si raspunzi DOAR pe baza ghidurilor gasite. Dai sfaturi concrete, aplicate "
    "pe situatia utilizatorului, intr-un ton prietenos si incurajator. La final "
    "spui din ce ghiduri ai luat informatia (titlurile dintre parantezele "
    "drepte). Daca ghidurile nu acopera subiectul, spui clar asta - nu inventa. "
    "Raspunzi scurt, in romana."
)

llm = ChatOpenAI(model="gpt-4.1-mini", api_key=OPEN_API_KEY)

agent = create_agent(
    llm,
    tools=[cauta_in_ghiduri],
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






















