from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, select

from models import ChatInDB, ChatUserAssociation
from db import db_helper
from .schemas import ChatSchema


async def get_chat_user_association(
    chat_id: int,
    user_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    stmt = select(ChatUserAssociation).where(
        ChatUserAssociation.chat_id == chat_id,
        ChatUserAssociation.user_id == user_id,
    )
    chat_user_association = await session.execute(stmt).one_or_none()
    if chat_user_association is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you do not have access to this chat or chat not found",
        )


async def get_chat(
    chat_info: ChatSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    stmt = select(ChatInDB).where(ChatInDB.chat_id_in_mongodb == chat_info.chat_id).limit(1)
    result: Result = await session.execute(stmt)
    chat_from_db = result.one_or_none()

    if chat_from_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"chat {chat_info.chat_id} not found",
        )
    return chat_from_db[0]
