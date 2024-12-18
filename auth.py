import jwt
from datetime import datetime, timedelta
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import os

# Secret key for signing JWT
SECRET_KEY = os.urandom(32)  # chave de criptografia segura

# Function to generate a JWT token
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token expira em 1 hora
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Function to decode and verify a JWT token
def verify_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
