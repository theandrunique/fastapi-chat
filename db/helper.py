from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)

from core.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool) -> None:
        self.enginge = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.enginge,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def __get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.__get_scoped_session()
        try:
            yield session
        finally:
            await session.close()


db_helper = DatabaseHelper(
    url=settings.DATABASE_URI,
    echo=settings.DB_ECHO,
)
