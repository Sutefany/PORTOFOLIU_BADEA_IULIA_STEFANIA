
############################### "MESAGERUL" dintre STREAMLIT si API-ul aplicatiei ###############################

# Functia api(...) construieste cererea HTTP, o trimite catre API, asteapta raspunsul (20x, 30x, 40x sau 50x) si verifica
# erorile ( de validare sau daca timpul este prea mare). Daca cererea reuseste, returneaza rezultatul catre Streamlit.

import requests

API_URL = "http://127.0.0.1:8000"

def api(metoda: str, cale: str, timeout: int = 5, **kwargs):
    try:
        r = requests.request(metoda, f"{API_URL}{cale}", timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError:
        return False, "Nu pot contacta API-ul. Ai pornit `pp3_app.py` intr-un alt terminal?"
    except requests.exceptions.Timeout:
        return False, "API-ul a raspuns prea greu (timeout)."

    if r.status_code >= 400:
        try:
            detaliu = r.json().get("detail", r.text)
        except ValueError:
            return False, r.text

        if isinstance(detaliu, list):
            mesaje = []
            for e in detaliu:
                camp = ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path"))
                mesaje.append(f"{camp}: {e['msg']}")
            return False, "; ".join(mesaje)
        return False, str(detaliu)

    return True, (r.json() if r.content else None)