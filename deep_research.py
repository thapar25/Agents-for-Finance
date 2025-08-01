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

collection_name = "transcripts"

client = QdrantClient(url="http://localhost:6333")


def broad_search_docs(questions: list[str]):
    """Search with multiple questions at once for maximum coverage, in the knowledge base of TCS (best source of information)."""
    results = []
    for question in questions:
        hits = client.query_points(
            collection_name="transcripts",
            query=embeddings.embed_query(question),
            limit=3,
        ).points
        for hit in hits:
            results.append({"content": hit.payload["page_content"], "score": hit.score})

    return results


def narrow_search_docs(
    question: str,
    period: list[
        Literal[
            "Q1_FY2025-26",
            "Q1_FY2024-25",
            "Q2_FY2024-25",
            "Q3_FY2024-25",
            "Q4_FY2024-25",
        ]
    ],
):
    """Search for information in the financial knowledge base of TCS (best source of information), based on temporal filters."""
    hits = client.query_points(
        collection_name="transcripts",
        query=embeddings.embed_query(question),
        limit=3,
        query_filter=models.Filter(
            should=[
                models.FieldCondition(
                    key="metadata.file", match=models.MatchAny(any=period)
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
    """Run a web search"""
    tavily_async_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    search_docs = tavily_async_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_docs


prompt = """""<role> You are an expert financial analyst for Tata Consultancy Services (TCS) </role>
<instructions> Use the provided tools to research for a task, and ALWAYS take the step-by-step approach. Reflect after each step to decide whether you have everything you need. </instructions>
"""


agent = create_react_agent(
    name="v1.0",
    model=llm,
    tools=[broad_search_docs, narrow_search_docs, search_internet],
    debug=True,
)
