from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, select

from models import ChatInDB
from db import db_helper
from .schemas import ChatSchema


async def get_chat_dependency(
    chat_info: ChatSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    stmt = select(ChatInDB).where(ChatInDB.id == chat_info.chat_id).limit(1)
    result: Result = await session.execute(stmt)
    chat_from_db = result.one_or_none()

    if chat_from_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"chat {chat_info.chat_id} not found",
        )
    return chat_from_db[0]
