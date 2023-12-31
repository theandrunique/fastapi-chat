from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result

from models import ChatUserAssociation, ChatInDB
from models.user import UserInDB


async def add_user_to_chat(
    session: AsyncSession,
    chat_id: int,
    user_id: int,
):
    chat_user_association = ChatUserAssociation(
        chat_id=chat_id,
        user_id=user_id,
    )

    session.add(chat_user_association)
    await session.commit()

    return chat_user_association


async def remove_user_from_chat(
    session: AsyncSession,
    chat_user_association: ChatUserAssociation,
):
    await session.delete(chat_user_association)
    await session.commit()


async def get_chat_user_association(
    chat_id: int,
    user_id: int,
    session: AsyncSession,
):
    stmt = select(ChatUserAssociation).where(
        ChatUserAssociation.chat_id == chat_id,
        ChatUserAssociation.user_id == user_id,
    )
    chat_user_association = await session.execute(stmt)
    chat_user_association = chat_user_association.one_or_none()
    return chat_user_association[0]


async def get_chat_by_id(
    session: AsyncSession,
    chat_id: int,
):
    stmt = select(ChatInDB).where(ChatInDB.id == chat_id).limit(1)
    result: Result = await session.execute(stmt)
    chat_from_db = result.one_or_none()

    return chat_from_db


async def get_users_of_chat(
    session: AsyncSession,
    chat_id: int,
) -> list[UserInDB]:
    stmt = (
        select(ChatUserAssociation, UserInDB)
        .join(UserInDB)
        .where(ChatUserAssociation.chat_id == chat_id)
    )

    result: Result = await session.execute(stmt)

    return [user for _, user in result]


async def change_chat_title(
    session: AsyncSession,
    chat: ChatInDB,
    new_title: int,
):
    chat.title = new_title
    session.add(chat)
    await session.commit()


async def delete_chat(
    session: AsyncSession,
    chat: ChatInDB,
):
    await session.delete(chat)
    await session.commit()
