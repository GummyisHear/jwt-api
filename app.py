from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Flask, jsonify, request
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

SALAVOTI = os.environ["JWT_SALAVOTI"]

KASUTAJAD = {
    "mari": {"parool": "maasikas1", "id": "1024", "role": "student"},
    "juhan": {"parool": "admin123", "id": "1", "role": "admin"},
}


@app.post("/login")
def login():
    andmed = request.get_json(silent=True) or {}
    kasutajanimi = andmed.get("kasutajanimi")
    kasutaja = KASUTAJAD.get(kasutajanimi)
    if not kasutaja or kasutaja["parool"] != andmed.get("parool"):
        return jsonify(viga="Vale kasutajanimi või parool"), 401

    nuud = datetime.now(timezone.utc)
    payload = {
        "sub": kasutaja["id"],
        "name": kasutajanimi,
        "role": kasutaja["role"],
        "iat": nuud,
        "exp": nuud + timedelta(minutes=5),
    }
    token = jwt.encode(payload, SALAVOTI, algorithm="HS256")
    return jsonify(token=token)


def noua_tokenit(roll=None):
    """Require a valid Bearer token; optionally require a specific role."""

    def dekoraator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            pais = request.headers.get("Authorization", "")
            if not pais.startswith("Bearer "):
                return jsonify(viga="Token puudub"), 401
            try:
                # Only allow HS256 -> protects against the `alg: none` attack
                andmed = jwt.decode(pais[7:], SALAVOTI, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return jsonify(viga="Token on aegunud"), 401
            except jwt.InvalidTokenError:
                return jsonify(viga="Vigane token"), 401
            if roll and andmed.get("role") != roll:
                return jsonify(viga="Õigused puuduvad"), 403
            return f(andmed, *args, **kwargs)

        return wrapper

    return dekoraator


@app.get("/profiil")
@noua_tokenit()
def profiil(andmed):
    return jsonify(andmed)


@app.get("/admin")
@noua_tokenit(roll="admin")
def admin(andmed):
    return jsonify(teade=f"Tere, admin {andmed['name']}!")


if __name__ == "__main__":
    app.run(debug=True)