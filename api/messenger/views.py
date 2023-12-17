from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from models import (
    ChatInDB,
    UserInDB,
    ChatType,
    ChatUserAssociation,
)
from api.auth import utils as auth_utils
from db import db_helper
from mongodb import ChatInMongoDB

from .schemas import (
    ChatInfoSchemaOut,
    ChatSchema,
    CreateChatSchema,
    GetChatMessages,
)
from . import utils
from . import crud

router = APIRouter(prefix="/chat")


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

    chat_user_association = ChatUserAssociation(
        user_id=current_user.id, chat_id=new_chat_in_db.id
    )

    session.add(chat_user_association)
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
            detail=f"user {user_id} not found or already exists in chat",
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


@router.get("/get_chat_messages")
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


@router.get("/get_chat_info", response_model=ChatInfoSchemaOut)
async def get_chat_info(
    chat_info: ChatSchema,
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
):
    chat_in_mongodb = ChatInMongoDB(
        user_id=current_user.id,
        chat_id=chat_info.chat_id,
    )
    users_of_chat = await crud.get_users_of_chat(
        session=session,
        chat_id=chat_info.chat_id,
    )
    chat_in_db = await crud.get_chat_by_id(
        session=session,
        chat_id=chat_info.chat_id,
    )

    return {
        "total_messages": chat_in_mongodb.get_count_chat_messages(),
        "chat_participants": users_of_chat,
        "chat_info": chat_in_db,
    }
