from sqlalchemy.ext.asyncio import AsyncSession

from models import ChatUserAssociation


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
