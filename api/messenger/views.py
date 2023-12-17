from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models import ChatInDB, UserInDB, ChatType
from api.auth import utils as auth_utils
from db import db_helper
from mongodb import ChatInMongoDB

from .schemas import ChatSchema, CreateChatSchema, GetChatMessages
from . import utils
from . import crud

router = APIRouter(prefix="/messenger")


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

    return {
        "status": "success",
        "chat_id": new_chat_in_db.id,
    }


@router.post("/add_user")
async def add_user_to_chat(
    user_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    chat_id_db: ChatInDB = Depends(utils.get_chat_dependency),
):
    if chat_id_db.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have access to do that",
        )
    try:
        await crud.add_user_to_chat(
            session=session,
            chat_id=chat_id_db.id,
            user_id=user_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user {user_id} not found",
        )
    return {"status": "success"}


@router.post("/send_message")
async def send_message(
    message: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    chat_in_db: ChatInDB = Depends(utils.get_chat_dependency),
):
    chat_in_mongodb = ChatInMongoDB(
        user_id=current_user.id,
        chat_id=chat_in_db.id,
    )
    new_message = chat_in_mongodb.send_message(message=message)

    await utils.get_chat_user_association(
        chat_id=chat_in_db.id,
        user_id=current_user.id,
        session=session,
    )

    return new_message
