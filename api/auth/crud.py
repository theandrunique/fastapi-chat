from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserInDB
from .schemas import UserRegSchemaIn
from core import security


async def get_user_by_id(session: AsyncSession, id: int) -> UserInDB:
    return await session.get(UserInDB, ident=id)


async def create_user(
    session: AsyncSession,
    user_data: UserRegSchemaIn,
) -> UserInDB:
    user_data.password = security.hash_password(user_data.password)
    new_user = UserInDB(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_by_login(
    session: AsyncSession,
    login: str,
) -> UserInDB:
    stmt = select(UserInDB).where(UserInDB.login == login)
    result: Result = await session.execute(stmt)
    user = result.scalars().one_or_none()
    return user
