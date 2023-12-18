from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ChatType, ChatInDB, ChatUserAssociation


async def create_new_group_chat(
    session: AsyncSession,
    title: str,
    creator_id: int,
):
    new_chat_in_db = ChatInDB(
        title=title,
        creator_id=creator_id,
        type=ChatType.GROUP,
    )

    session.add(new_chat_in_db)
    await session.commit()

    chat_user_association = ChatUserAssociation(
        chat_id=new_chat_in_db.id,
        user_id=creator_id,
    )

    session.add(chat_user_association)
    await session.commit()

    return new_chat_in_db


async def get_my_chats(
    user_id: int,
    session: AsyncSession,
):
    stmt = (
        select(ChatUserAssociation, ChatInDB)
        .join(ChatInDB)
        .where(ChatUserAssociation.user_id == user_id)
    )
    result: Result = await session.execute(stmt)

    return [chat for _, chat in result]
