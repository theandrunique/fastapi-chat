from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from . import utils
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
    session: AsyncSession = Depends(db_helper.get_scoped_session),
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

    if utils.validate_password(
        user_data.password,
        hashed_password=user_from_db.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect login or password",
        )

    jwt_payload = {
        "sub": user_from_db.id,
        "login": user_from_db.login,
    }
    token = security.create_access_token(subject=jwt_payload)
    return TokenSchema(
        access_token=token,
        token_type="Bearer",
    )


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegSchemaOut,
)
async def register_user(
    user_data: UserRegSchemaIn,
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    try:
        new_user = await crud.create_user(
            session=session,
            user_data=user_data,
        )
    except IntegrityError:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user with this login already exists",
        )
    return UserRegSchemaOut(
        id=new_user.id,
        login=new_user.login,
    )
