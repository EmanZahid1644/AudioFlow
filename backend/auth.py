from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re

# =========================
# Load Environment Variables
# =========================

load_dotenv()

# =========================
# Password Hashing Setup
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =========================
# JWT Settings
# =========================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "audioflow_secret_key_change_later"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 24

# =========================
# Hash Password
# =========================

def hash_password(password: str):
    return pwd_context.hash(password)

# =========================
# Verify Password
# =========================

def verify_password(
    plain_password,
    hashed_password
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# =========================
# Strong Password Validation
# =========================

def validate_password(password):

    if len(password) < 8:
        return False, "Password must contain at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password needs one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password needs one lowercase letter"

    if not re.search(r"[0-9]", password):
        return False, "Password needs one number"

    if not re.search(r"[@#$%^&*!]", password):
        return False, "Password needs one special character"

    return True, "Strong password"

# =========================
# Create JWT Token
# =========================

def create_token(email):

    expire_time = datetime.utcnow() + timedelta(
        hours=ACCESS_TOKEN_EXPIRE_HOURS
    )

    payload = {
        "sub": email,
        "exp": expire_time
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

# =========================
# Verify JWT Token
# =========================

def verify_token(token):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload.get("sub")

    except JWTError:

        return None