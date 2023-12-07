import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_access_token
from models.user import UserInDB
from . import crud
from db import db_helper


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


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/demo-auth/jwt/login/",
)


async def validate_access_token(
    token: str = Depends(oauth2_scheme),
) -> dict:
    """token validation"""

    try:
        payload = verify_access_token(
            access_token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token",
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(validate_access_token),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserInDB:
    """checking that user exists"""

    user_id: str | None = payload.get("sub")

    if user := await crud.get_user_by_id(
        session=session,
        id=user_id,
    ):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token (user not found)",
    )


async def get_current_active_auth_user(
    user: UserInDB = Depends(get_current_auth_user),
) -> UserInDB:
    """checking that user is active"""

    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive",
    )
