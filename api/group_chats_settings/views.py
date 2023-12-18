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
)
from api.group_chats import utils as chats_utils
from api.auth import utils as auth_utils
from db import db_helper
from mongodb import ChatInMongoDB

from .schemas import (
    ChatInfoSchemaOut,
)
from . import utils
from . import crud


router = APIRouter(prefix="/chat-settings")


@router.post("/add-user")
async def add_user_to_chat(
    user_id: int,
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
    chat_in_db: ChatInDB = Depends(utils.get_chat_dependency),
):
    if chat_in_db.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have access to do that",
        )
    try:
        await crud.add_user_to_chat(
            session=session,
            chat_id=chat_in_db.id,
            user_id=user_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user {user_id} not found or already exists in chat",
        )
    return {"status": "success"}


@router.delete("/delete-user")
async def remove_user_from_chat(
    user_id: int,
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
    chat_in_db: ChatInDB = Depends(utils.get_chat_dependency),
):
    if chat_in_db.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have access to do that",
        )

    chat_user_association = await crud.get_chat_user_association(
        chat_id=chat_in_db.id,
        user_id=user_id,
        session=session,
    )

    if not chat_user_association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    await crud.remove_user_from_chat(
        session=session,
        chat_user_association=chat_user_association[0],
    )

    return {"status": "success"}


@router.get("/get-chat-info", response_model=ChatInfoSchemaOut)
async def get_chat_info(
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    chat_in_db: ChatInDB = Depends(chats_utils.get_chat_dependency),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    await chats_utils.get_chat_user_association(
        chat_id=chat_in_db.id,
        user_id=current_user.id,
        session=session,
    )

    chat_in_mongodb = ChatInMongoDB(
        user_id=current_user.id,
        chat_id=chat_in_db.id,
    )
    users_of_chat = await crud.get_users_of_chat(
        session=session,
        chat_id=chat_in_db.id,
    )

    return {
        "total_messages": chat_in_mongodb.get_count_chat_messages(),
        "chat_members": users_of_chat,
        "chat_info": chat_in_db,
    }


@router.patch("/update-chat-title")
async def update_chat_title(
    new_title: str,
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    chat_in_db: ChatInDB = Depends(chats_utils.get_chat_dependency),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    if chat_in_db.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have access to do that",
        )

    await crud.change_chat_title(
        session=session,
        chat=chat_in_db,
        new_title=new_title,
    )

    return {"status": "success"}


@router.delete("/delete-chat")
async def delete_chat(
    current_user: UserInDB = Depends(auth_utils.get_current_active_auth_user),
    chat_in_db: ChatInDB = Depends(chats_utils.get_chat_dependency),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    if chat_in_db.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have access to do that",
        )

    await crud.delete_chat(session=session, chat=chat_in_db)

    return {"status": "success"}
