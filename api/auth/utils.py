from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import verify_access_token
from models.user import UserInDB
from .crud import get_user_by_id
from db import db_helper


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
            detail=f"Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_auth_user(
    payload: dict = Depends(validate_access_token),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> UserInDB:
    """checking that user exists"""

    sub: str | None = payload.get("sub")

    if user := await get_user_by_id(
        session=session,
        id=sub.get("user_id"),
    ):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
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
