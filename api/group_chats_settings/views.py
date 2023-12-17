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
from api.auth import utils as auth_utils
from db import db_helper
from mongodb import ChatInMongoDB

from .schemas import (
    ChatInfoSchemaOut,
    ChatSchema,
)
from . import utils
from . import crud


router = APIRouter(prefix="/chat-settings")

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