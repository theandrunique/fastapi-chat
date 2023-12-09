from datetime import datetime, timedelta

import bcrypt
import jwt

from core.config import settings

ALGORITHM = "HS256"


def create_access_token(
    subject: str,
    expires_delta=None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
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
