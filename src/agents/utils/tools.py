from agents.utils.services import (
    perform_tavily_search,
    multiquery_vector_search,
    filtered_vector_search,
)
from agents.utils.models import Collection, Quarters


async def search_internet(
    query: str,
    max_results: int = 5,
    topic: str = "finance",
    include_raw_content: bool = False,
):
    """Fallback search via the internet. Use **only** if TCS knowledge base yields no relevant results."""
    return await perform_tavily_search(query, max_results, topic, include_raw_content)


async def search_wide(questions: list[str], collection_name: Collection):
    """Perform a broad multi-query search across the TCS knowledge base for maximum information coverage."""
    return await multiquery_vector_search(questions, collection_name)


async def search_focused(
    question: str,
    collection_name: Collection,
    quarters: list[Quarters],
    top_k: int = 4,
):
    """Perform a targeted search in the TCS financial knowledge base, filtered by fiscal quarters. Returns top-k results."""
    return await filtered_vector_search(question, collection_name, quarters, top_k)


tools = [search_focused, search_wide, search_internet]
