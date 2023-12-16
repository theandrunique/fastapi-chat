from datetime import datetime, timedelta
import time

import bcrypt
import jwt

from core.config import settings

ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    expires_delta: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta
    )
    encoded_jwt = jwt.encode(
        payload={"exp": expire, "sub": subject},
        key=settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_access_token(access_token: str):
    data = jwt.decode(
        jwt=access_token,
        key=settings.SECRET_KEY,
        algorithms=[ALGORITHM],
    )
    return data


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
