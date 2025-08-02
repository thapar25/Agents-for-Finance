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
from pydantic import ValidationError
from agents.utils.sql_models import Log, AgentResponse, AsyncSessionLocal

load_dotenv()


# Initialize Qdrant client
client = AsyncQdrantClient(url="http://localhost:6333")
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
    model_name = None
    structured_cols = None
    p_tokens, c_tokens, t_tokens = None, None, None

    try:
        # Use Pydantic to parse and validate the entire response structure
        parsed_response = AgentResponse.model_validate(agent_output["response"])

        # Extract structured response keys
        structured_cols = parsed_response.get_structured_response_keys()

        # Extract metadata from the final AI message
        final_metadata = parsed_response.get_final_metadata()
        if final_metadata:
            model_name = final_metadata.model_name
            if final_metadata.token_usage:
                p_tokens = final_metadata.token_usage.prompt_tokens
                c_tokens = final_metadata.token_usage.completion_tokens
                t_tokens = final_metadata.token_usage.total_tokens

    except (ValidationError, KeyError, IndexError) as e:
        print(f"Could not parse agent_output for metadata: {e}")
        # Continue with null values for the new fields

    try:
        # Create an instance of the SQLAlchemy Log model
        log_entry = Log(
            session_id=session_id,
            user_input=user_input,
            agent_output=json.dumps(agent_output, default=str),  # Store the full JSON
            start_time=start_time,
            end_time=end_time or datetime.now(),
            created_at=created_at or datetime.now(),
            model_name=model_name,
            structured_output_columns=structured_cols,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
            total_tokens=t_tokens,
        )

        # Add the new log entry to the database
        async with AsyncSessionLocal() as session:
            session.add(log_entry)
            await session.commit()

    except Exception as e:
        print(f"Error logging to MySQL with SQLAlchemy: {e}")
