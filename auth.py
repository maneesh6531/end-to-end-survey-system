# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()

# passlib sometimes tries to read ``bcrypt.__about__.__version__`` when
# determining whether the installed bcrypt library is compatible.  Older
# releases (e.g. 5.0.0) omit the ``__about__`` attribute which triggers
# an AttributeError during hashing; this shim ensures the attribute exists
# so the exception is avoided.  Upgrading bcrypt to a newer version is the
# preferred long‑term fix, but the shim is harmless in the meantime.
import bcrypt
import types
# the shim below is no longer strictly necessary since we don't use
# passlib, but keeping it doesn't hurt in case something else reads the
# attribute.
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = types.SimpleNamespace(__version__=bcrypt.__version__)

SECRET_KEY                = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM                 = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1 hour

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    """Hash a password using the bcrypt library directly.

    The underlying C implementation only considers the first 72 bytes of
    input; any extra bytes are ignored but some versions raise an
    exception when given a longer value.  We therefore truncate the UTF‑8
    encoding to 72 bytes before calling ``hashpw`` and ``checkpw``.
    """
    pw = password.encode("utf-8") if isinstance(password, str) else password
    if len(pw) > 72:
        pw = pw[:72]
    # bcrypt.hashpw returns bytes, so decode for storage convenience
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode("utf-8") if isinstance(plain, str) else plain
    if len(pw) > 72:
        pw = pw[:72]
    return bcrypt.checkpw(pw, hashed.encode("utf-8"))


def create_access_token(data: dict):
    to_encode = data.copy()
    expire    = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role     = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(user: dict = Depends(verify_token)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
