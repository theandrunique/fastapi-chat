from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import (
    UserRegSchemaIn,
    UserRegSchemaOut,
    UserSchema,
    TokenSchema,
)
from . import crud
from db import db_helper
from core import security


router = APIRouter(prefix="/auth")


@router.post("/login/", response_model=TokenSchema)
async def auth_user(
    user_data: UserSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    user_from_db = await crud.get_user_by_login(
        session=session,
        login=user_data.login,
    )
    if not user_from_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )

    if not security.validate_password(
        user_data.password,
        hashed_password=user_from_db.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect login or password",
        )

    token = security.create_access_token(
        subject={
            "user_id": user_from_db.id,
            "login": user_from_db.login,
        }
    )
    return TokenSchema(
        access_token=token,
        token_type="Bearer",
    )


@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=UserRegSchemaOut)
async def register_user(
    user_data: UserRegSchemaIn,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    try:
        new_user = await crud.create_user(
            session=session,
            user_data=user_data,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user with this login already exists",
        )
    return UserRegSchemaOut(
        id=new_user.id,
        login=new_user.login,
    )
