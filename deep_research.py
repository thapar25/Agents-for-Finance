import os
from typing import Literal

from tavily import TavilyClient

from langgraph.prebuilt import create_react_agent

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from qdrant_client import QdrantClient, models


load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

client = QdrantClient(url="http://localhost:6333")


def search_wide(questions: list[str],  collection_name : Literal["transcripts", "reports"]):
    """Perform a broad multi-query search across the TCS knowledge base for maximum information coverage."""
    results = []
    for question in questions:
        hits = client.query_points(
            collection_name=collection_name,
            query=embeddings.embed_query(question),
            limit=3,
        ).points
        for hit in hits:
            results.append({"content": hit.payload["page_content"], "score": hit.score})

    return results


def search_focused(
    question: str,
    collection_name : Literal["transcripts", "reports"],
    quarters: list[
        Literal[
            "Q1_FY2025-26",
            "Q1_FY2024-25",
            "Q2_FY2024-25",
            "Q3_FY2024-25",
            "Q4_FY2024-25",
        ]
    ],
    top_k: int = 4,
   
):
    """Perform a targeted search in the TCS financial knowledge base, filtered by fiscal quarters. Returns top-k results."""
    hits = client.query_points(
        collection_name=collection_name,
        query=embeddings.embed_query(question),
        limit=top_k,
        query_filter=models.Filter(
            should=[
                models.FieldCondition(
                    key="metadata.file", match=models.MatchAny(any=quarters)
                )
            ]
        ),
    ).points
    results = []
    for hit in hits:
        results.append({"content": hit.payload["page_content"], "score": hit.score})
    return results


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


# Search tool to use to do research
def search_internet(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "finance",
    include_raw_content: bool = False,
):
    """Fallback search via the internet. Use **only** if TCS knowledge base yields no relevant results."""
    tavily_async_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    search_docs = tavily_async_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_docs


prompt = """""<role> You are an expert financial analyst for Tata Consultancy Services (TCS) </role>
<instructions> You have access to 'reports' for Financial Reports and 'transcripts' to go through Earning Call Conference transcripts data. Use the provided tools to research for a task, and ALWAYS take the step-by-step approach. Reflect after each step to decide whether you have everything you need. </instructions>
<additional_info> The ongoing fiscal period in India is Q2_FY2025-26 <additional_info>
"""


agent = create_react_agent(
    name="v1.1",
    model=llm,
    tools=[search_focused, search_wide, search_internet],
    debug=True,
)
