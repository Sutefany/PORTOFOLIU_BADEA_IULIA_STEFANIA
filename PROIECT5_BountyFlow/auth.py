import datetime
from zoneinfo import ZoneInfo

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from model import get_db, gaseste_user_dupa_username

SECRET_KEY = "cheie-secreta-doar-pentru-curs-nu-o-pune-niciodata-in-cod-real"
ALGORITHM = "HS256"
EXPIRARE_MINUTE = 60


# #############################################################
# PARTEA 1 - PAROLE
# #############################################################

def hash_parola(parola: str) -> str:
    return bcrypt.hashpw(parola.encode(), bcrypt.gensalt()).decode()

def verifica_parola(parola: str, hash_salvat: str) -> bool:
    return bcrypt.checkpw(parola.encode(), hash_salvat.encode())

# #############################################################
# PARTEA 2 - JWT
# #############################################################

def creeaza_token(username: str) -> str:
   acum = datetime.datetime.now(datetime.timezone.utc).astimezone(ZoneInfo("Europe/Bucharest"))
   payload = {"sub": username, "exp": acum + datetime.timedelta(minutes=EXPIRARE_MINUTE)}
   return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodeaza_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload["sub"]

bearer_scheme = HTTPBearer(auto_error=False)

# #############################################################
# PARTEA 3 - get_current_user
# #############################################################

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db=Depends(get_db)):
    eroare_neautorizat = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autentificare necesara (Authorization: Bearer <token>)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise eroare_neautorizat

    try:
        username = decodeaza_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Tokenul a expirat - autentifica-te din nou")
    except jwt.InvalidTokenError:
        raise eroare_neautorizat

    user = gaseste_user_dupa_username(db, username)
    if user is None:
        raise eroare_neautorizat

    return user