# =============================================================
# RAG  -  indexul Chroma al fiselor
# =============================================================

import chromadb
from chromadb.utils import embedding_functions
from session28.date import OPEN_API_KEY

# #############################################################
# PARTEA 0 - COLECTIA CHROMA
# #############################################################

functie_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPEN_API_KEY,
    model_name="text-embedding-3-small"
)

client = chromadb.Client()
colectie = client.create_collection(
    name="s50_fise",
    embedding_function=functie_embedding,
)

# #############################################################
# PARTEA 1 - INDEXARE  (plan: 3.1)
# #############################################################

def indexeaza_fisa(fisa):
    colectie.add(ids=[str(fisa.id)], documents=[fisa.continut], metadatas=[{"titlu": fisa.titlu}] )

def indexeaza_toate(fise):
    for fisa in fise:
        indexeaza_fisa(fisa)

def sterge_din_index(fisa_id):
    colectie.delete(ids=[str(fisa_id)])

# #############################################################
# PARTEA 2 - CAUTARE  (plan: 3.2)
# #############################################################

def cauta(intrebare, n_rezultate=2):
    rezultat = colectie.query(query_texts=[intrebare], n_results=n_rezultate)
    texte = rezultat['documents'][0]
    metadatas = rezultat['metadatas'][0]
    distante = rezultat['distances'][0]

    lista = []
    for i in range(len(texte)):
        lista.append(
            {
                'titlu': metadatas[i]["titlu"],
                'text': texte[i],
                'distanta': round(distante[i],3)
             }
        )
    return lista
