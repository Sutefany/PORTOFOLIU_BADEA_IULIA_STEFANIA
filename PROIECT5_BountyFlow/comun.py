import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

def api(metoda: str, cale: str, cu_token: bool = True, timeout=5, **kwargs):
    headers = {}
    if cu_token:
        headers["Authorization"] = f"Bearer {st.session_state.get('token')}"
    try:
        r = requests.request(metoda, f"{API_URL}{cale}", headers=headers, timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError:
        return False, "Nu pot contacta API-ul. Ai pornit intr-un alt terminal?"
    except requests.exceptions.Timeout:
        return False, "API-ul a raspuns prea greu (timeout)."

    if r.status_code == 401:
        st.session_state.token = None
        st.session_state.username = None
        return False, "Sesiune expirata sau nevalida - te rugam sa te loghezi din nou."

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