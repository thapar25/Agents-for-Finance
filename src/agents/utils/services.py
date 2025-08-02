# Services for MySQL logging and Search Operations
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client import models
from langchain_openai import OpenAIEmbeddings
from tavily.async_tavily import AsyncTavilyClient
from dotenv import load_dotenv
import os
import asyncio
import json
from datetime import datetime
from typing import Literal
from agents.utils.models import Collection, Quarters
from pydantic import BaseModel
from agents.utils.sql_models import Log, AsyncSessionLocal
from langchain_core.messages import messages_to_dict


load_dotenv()


# Initialize Qdrant client
client = AsyncQdrantClient(url=os.environ["QDRANT_URL"])
# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


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


def serialize_agent_response(agent_response_data: dict) -> dict:
    """
    Converts a LangChain agent response containing class instances
    (like AIMessage) into a JSON-serializable dictionary.
    """
    serialized_data = {}

    # Serialize the 'messages' list using LangChain's utility
    if "messages" in agent_response_data:
        serialized_data["messages"] = messages_to_dict(agent_response_data["messages"])

    # Serialize the 'structured_response' if it's a Pydantic model
    if "structured_response" in agent_response_data:
        sr = agent_response_data["structured_response"]
        if isinstance(sr, BaseModel):
            # Use .model_dump() for modern Pydantic models
            serialized_data["structured_response"] = sr.model_dump(mode="json")
        else:
            # Pass it through if it's already a dict or something else
            serialized_data["structured_response"] = sr

    # Copy any other keys that might exist
    for key, value in agent_response_data.items():
        if key not in serialized_data:
            serialized_data[key] = value

    return serialized_data


async def log_to_db(
    session_id: str,
    user_input: str,
    agent_output: dict,  # Expects the serialized dictionary
    start_time: datetime = None,
    end_time: datetime = None,
):
    """
    Logs the entire agent response as a single JSON string to the database.
    """
    try:
        # Create an instance of the simple SQLAlchemy Log model
        log_entry = Log(
            session_id=session_id,
            user_input=user_input,
            # Convert the entire dictionary to a JSON string for storage
            agent_output=json.dumps(agent_output, default=str),
            start_time=start_time,
            end_time=end_time or datetime.now(),
        )

        async with AsyncSessionLocal() as session:
            session.add(log_entry)
            await session.commit()

    except Exception as e:
        print(f"Error logging to MySQL with SQLAlchemy: {e}")
