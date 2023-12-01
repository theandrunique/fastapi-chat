from core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


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


db_helper = DatabaseHelper(
    url=settings.DATABASE_URI,
    echo=settings.DB_ECHO,
)
