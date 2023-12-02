from datetime import datetime, timedelta
import hashlib
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
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(access_token):
    data = jwt.decode(access_token, settings.SECRET_KEY, algorithm=ALGORITHM)
    return data


def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
