from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    ChatInDB,
    UserInDB,
)
from api.auth import utils as auth_utils
from db import db_helper
from mongodb import ChatInMongoDB

from .schemas import (
    CreateChatSchema,
    GetChatMessages,
)
from . import utils
from . import crud
router = APIRouter(prefix="/chat")


@router.post("/create-chat")
async def create_chat(
    chat_conf: CreateChatSchema,
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    new_chat_in_db = await crud.create_new_group_chat(
        session=session,
        title=chat_conf.title,
        creator_id=current_user.id,
    )

    return {
        "status": "success",
        "chat_id": new_chat_in_db.id,
    }


@router.post("/send-message")
async def send_message(
    message: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    chat_in_db: ChatInDB = Depends(utils.get_chat_dependency),
):
    await utils.get_chat_user_association(
        chat_id=chat_in_db.id,
        user_id=current_user.id,
        session=session,
    )
    
    chat_in_mongodb = ChatInMongoDB(
        user_id=current_user.id,
        chat_id=chat_in_db.id,
    )
    new_message = chat_in_mongodb.send_message(message=message)

    return new_message


@router.get("/get-chat-messages")
async def get_chat_messages(
    query_info: GetChatMessages,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
):
    await utils.get_chat_user_association(
        chat_id=query_info.chat_id,
        user_id=current_user.id,
        session=session,
    )

    chat_in_mongodb = ChatInMongoDB(
        user_id=current_user.id,
        chat_id=query_info.chat_id,
    )
    messages = chat_in_mongodb.get_chat_messages(
        count=query_info.count,
        offset=query_info.offset,
    )
    return {
        "total_messages": chat_in_mongodb.get_count_chat_messages(),
        "chat_id": query_info.chat_id,
        "messages": messages,
    }
