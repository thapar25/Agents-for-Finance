# Services for MySQL logging and Search Operations
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client import models
from langchain_openai import OpenAIEmbeddings
from tavily.async_tavily import AsyncTavilyClient
from dotenv import load_dotenv
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import json
from datetime import datetime
from typing import Literal
from agents.utils.models import Collection, Quarters

load_dotenv()


# Initialize Qdrant client
client = AsyncQdrantClient(url="http://localhost:6333")
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Initialize MySQL engine for logging
mysql_username = os.getenv("DB_USER")
mysql_password = os.getenv("DB_PASSWORD")
mysql_host = os.getenv("DB_HOST", "localhost")
mysql_database = os.getenv("DB_NAME")

mysql_connection_string = (
    f"mysql+aiomysql://{mysql_username}:{mysql_password}@{mysql_host}/{mysql_database}"
)

mysql_engine = create_async_engine(mysql_connection_string)

AsyncSessionLocal = sessionmaker(
    mysql_engine, class_=AsyncSession, expire_on_commit=False
)


async def perform_tavily_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "finance",
    include_raw_content: bool = False,
):
    """Perform a search using Tavily API. Returns search results based on the query."""
    tavily_async_client = AsyncTavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    try:
        search_docs = await tavily_async_client.search(
            query=query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
        return search_docs
    except Exception as e:
        print(f"Error performing Tavily search: {e}")
        return []


async def multiquery_vector_search(questions: list[str], collection_name: Collection):
    """Perform a multi-query search across a collection."""
    try:
        tasks = []
        for question in questions:
            tasks.append(
                client.query_points(
                    collection_name=collection_name,
                    query=await embeddings.aembed_query(question),
                    limit=3,
                )
            )
        results_list = await asyncio.gather(*tasks)

        # Flatten and structure results
        results = []
        for result in results_list:
            for hit in result.points:
                results.append(
                    {"content": hit.payload["page_content"], "score": hit.score}
                )

        return results
    except Exception as e:
        raise Exception(f"Error in multiquery_vector_search: {e}")


async def filtered_vector_search(
    question: str,
    collection_name: Collection,
    quarters: list[Quarters],
    top_k: int = 4,
):
    """Perform a targeted search in the knowledge base, filtered by fiscal quarters. Returns top-k results."""
    try:
        query_filter = models.Filter(
            should=[
                models.FieldCondition(
                    key="metadata.file", match=models.MatchAny(any=quarters)
                )
            ]
        )

        hits = await client.query_points(
            collection_name=collection_name,
            query=await embeddings.aembed_query(question),
            limit=top_k,
            query_filter=query_filter,
        )

        # Structure results consistently
        results = []
        for hit in hits.points:
            results.append({"content": hit.payload["page_content"], "score": hit.score})

        return results
    except Exception as e:
        raise Exception(f"Error in filtered_vector_search: {e}")


async def log_to_db(
    session_id: str,
    user_input: str,
    agent_output: any,
    start_time: datetime = None,
    end_time: datetime = None,
    created_at: datetime = None,
):
    """
    Log agent input/output pair to MySQL logs table.

    Args:
        session_id: Session identifier
        user_input: User message/query
        agent_output: Agent response (string, list, dict, etc.)
        start_time: Start time of the session (optional)
        end_time: End time of the session (optional)
        created_at: Creation time of the log entry (optional)
    """
    try:
        async with AsyncSessionLocal() as session:
            # Convert output to JSON string if it's not a string
            if isinstance(agent_output, str):
                output_json = agent_output
            else:
                output_json = json.dumps(agent_output, default=str)

            # Prepare the SQL statement
            sql = text("""
                INSERT INTO logs (session_id, user_input, agent_output, start_time, end_time, created_at)
                VALUES (:session_id, :user_input, :agent_output, :start_time, :end_time, :created_at)
            """)
            # Execute the SQL statement
            await session.execute(
                sql,
                {
                    "session_id": session_id,
                    "user_input": user_input,
                    "agent_output": output_json,
                    "start_time": start_time,
                    "end_time": end_time or datetime.now(),
                    "created_at": created_at or datetime.now(),
                },
            )
            await session.commit()

    except Exception as e:
        print(f"Error logging to MySQL: {e}")
