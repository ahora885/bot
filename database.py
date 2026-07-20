import os

from dotenv import load_dotenv

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_async_engine(
    DATABASE_URL,
    echo=False
)


AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()


class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True
    )

    telegram_id = Column(
        Integer,
        unique=True,
        index=True
    )

    username = Column(
        String,
        nullable=True
    )

    first_name = Column(
        String,
        nullable=True
    )

    wallet = Column(
        Integer,
        default=0
    )

    welcome_bonus = Column(
        Boolean,
        default=False
    )

    free_test_count = Column(
        Integer,
        default=0
    )

    configs = Column(
        Integer,
        default=0
    )


async def create_tables():

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )
