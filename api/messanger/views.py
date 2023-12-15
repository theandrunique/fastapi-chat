from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models import ChatInDB, UserInDB, ChatType
from auth import utils as auth_utils
from db import db_helper
from mongodb import ChatInMongoDB

from .schemas import CreateChatSchema

router = APIRouter(prefix="")


@router.post("/create_chat")
async def create_chat(
    chat_conf: CreateChatSchema,
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    new_chat_in_db = ChatInDB(
        title=chat_conf.title,
        creator_id=current_user.id,
        type=ChatType.GROUP,
    )
    session.add(new_chat_in_db)
    await session.commit()

    chat_in_mongodb = ChatInMongoDB(
        user_id=current_user.id,
        chat_id=new_chat_in_db.chat_id_in_mongodb,
    )
