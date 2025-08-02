from datetime import datetime
from typing import Optional
import os
from sqlalchemy import DateTime, Text, String
from sqlalchemy.dialects.mysql import LONGTEXT

from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# Initialize MySQL engine for logging
mysql_username = os.getenv("DB_USER")
mysql_password = os.getenv("DB_PASSWORD")
mysql_host = os.getenv("DB_HOST", "localhost")
mysql_database = os.getenv("DB_NAME")

mysql_connection_string = (
    f"mysql+aiomysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}"
)


# Create the async engine and session factory
engine = create_async_engine(mysql_connection_string, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    user_input: Mapped[str] = mapped_column(Text)

    # Use LONGTEXT to ensure you can store very large JSON responses
    agent_output: Mapped[str] = mapped_column(LONGTEXT)

    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, index=True
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.now, index=True
    )


async def create_db_and_tables():
    """
    Run this function once to create the database tables.
    Deletes existing tables first.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")
