# ===========================================================================
# MINI-PROIECT: "Radar Biziday"  (Web Scraping) - Preluarea informatiilor
# ===========================================================================

# Preluarea unor informatii de pe site-ul de stiri BiziDay si transpunerea lor intr-o interfata web proprie
# LINK: https://www.biziday.ro/category/stiri/

import re
import requests
from bs4 import BeautifulSoup

URL = "https://www.biziday.ro/category/stiri/"
HEADERE = {"User-Agent": "curs-python-scraping/1.0 (exercitiu educativ, contact: curs@exemplu.ro)"}

TIPAR_METADATA = re.compile(r"([A-ZĂÂÎȘȚ][\wăâîșțĂÂÎȘȚ]*)\s*·\s*(\d{4}-\d{2}-\d{2})\s*@\s*(\d{2}:\d{2}:\d{2})\s*$")

def descompune_stirea(text, href):
    text = text.strip()
    potrivire = TIPAR_METADATA.search(text)
    if potrivire is None:
        return None

    sursa = potrivire.group(1)
    data = potrivire.group(2)
    ora = potrivire.group(3)
    continut = text[:potrivire.start()].strip()

    if not continut:
        return None
    return {"text": continut, "sursa": sursa, "data": data, "ora": ora, "url": href}

def stiri_de_pe_pagina(url):
    r = requests.get(url, headers=HEADERE, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    stiri = []

    container = soup.find_all('a')
    for stire in container:
        text = stire.get_text(" ", strip=True)
        href = stire.get("href")
        stire = descompune_stirea(text, href)
        if stire is not None:
            stiri.append(stire)
    return stiri

def sursa_cea_mai_frecventa(stiri):
    if not stiri:
        return None
    else:
        frecvente = {}
        for stire in stiri:
            sursa = stire['sursa']
            if sursa not in frecvente:
                frecvente[sursa] = 1
            else:
                frecvente[sursa] += 1
        cea_mai_frecventa = max(frecvente, key=frecvente.get)
        return cea_mai_frecventa, frecvente[cea_mai_frecventa]




