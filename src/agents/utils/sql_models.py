from datetime import datetime
from typing import List, Optional, Any, Dict
import os
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import create_async_engine, DateTime, Integer, Text, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

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


class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class ResponseMetadata(BaseModel):
    model_name: Optional[str] = None
    token_usage: Optional[TokenUsage] = None


class FinalAIMessage(BaseModel):
    """A Pydantic model specifically for the final AI message containing metadata."""

    type: str
    response_metadata: Optional[ResponseMetadata] = Field(
        None, alias="response_metadata"
    )


class StructuredResponse(BaseModel):
    """Represents the structured_response part of the JSON"""

    data: Dict[str, Any]

    @property
    def column_keys(self) -> Optional[str]:
        """Returns the top-level keys as a comma-separated string."""
        if self.data:
            return ",".join(self.data.keys())
        return None


class AgentResponse(BaseModel):
    """The Pydantic model for the entire agent output."""

    messages: List[Dict[str, Any]] = []
    structured_response: Optional[Dict[str, Any]] = None

    def get_final_metadata(self) -> Optional[ResponseMetadata]:
        """Finds the last AI message and returns its metadata."""
        if not self.messages:
            return None
        # The final AI message is typically the last one
        last_message_data = self.messages[-1]
        if last_message_data.get("type") == "ai":
            try:
                # Validate and parse just this message
                ai_message = FinalAIMessage.model_validate(last_message_data)
                return ai_message.response_metadata
            except ValidationError:
                return None
        return None

    def get_structured_response_keys(self) -> Optional[str]:
        """Gets the keys from the structured response."""
        if self.structured_response:
            return ",".join(self.structured_response.keys())
        return None


# --- SQLAlchemy ORM Model for the 'logs' Table ---


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    user_input: Mapped[str] = mapped_column(Text)
    agent_output: Mapped[str] = mapped_column(Text)  # Storing the full JSON output
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    model_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    structured_output_columns: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


async def create_db_and_tables():
    """
    Run this function once to create the database tables.
    Deletes existing tables first.
    """
    async with engine.begin() as conn:
        # Drop all tables and then recreate them.
        # Be careful with this in production!
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")
