import os
from typing import Literal

from tavily import TavilyClient

from deepagents import create_deep_agent

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

collection_name = "transcripts"

client = QdrantClient(url="http://localhost:6333")
vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)


def search_docs(question: str):
    """Search for information in the company X's earnings call data."""
    result = vector_store.similarity_search(question, k=3)
    return result


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


sub_research_prompt = """You are a dedicated researcher. Your job is to conduct research based on the users questions.

Conduct thorough research and then reply to the user with a detailed answer to their question"""

research_sub_agent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions. Only give this researcher one topic at a time. Do not pass multiple sub questions to this researcher. Instead, you should break down a large topic into the necessary components, and then call multiple research agents in parallel, one for each sub question.",
    "prompt": sub_research_prompt,
}

sub_critique_prompt = """You are a dedicated editor. You are being tasked to critique a report.

You can find the report at `final_report.md`.

You can find the question/topic for this report at `question.txt`.

The user may ask for specific areas to critique the report in. Respond to the user with a detailed critique of the report. Things that could be improved.

You can use the search tool to search for information, if that will help you critique the report

Do not write to the `final_report.md` yourself.

Things to check:
- Check that each section is appropriately named
- Check that the report is written as you would find in an essay or a textbook - it should be text heavy, do not let it just be a list of bullet points!
- Check that the report is comprehensive. If any paragraphs or sections are short, or missing important details, point it out.
- Check that the article covers key areas of the industry, ensures overall understanding, and does not omit important parts.
- Check that the article deeply analyzes causes, impacts, and trends, providing valuable insights
- Check that the article closely follows the research topic and directly answers questions
- Check that the article has a clear structure, fluent language, and is easy to understand.
"""

critique_sub_agent = {
    "name": "critique-agent",
    "description": "Used to critique the final report. Give this agent some infomration about how you want it to critique the report.",
    "prompt": sub_critique_prompt,
}


finance_instructions = """You are a financial research specialist. Your job is to conduct deep, qualitative research and produce a professional-grade report focused on financial performance, trends, and forward-looking insights.

Start by saving the original user request to `question.txt` for recordkeeping.

Use the `research-agent` to gather information. This may include earnings call transcripts, quarterly/annual financial reports, investor presentations, news coverage, and analyst commentary.

Once you have gathered sufficient insights, write your report to `final_report.md`.

You may call the `critique-agent` for feedback on your draft. Based on the critique, perform additional research or revise the report as needed. Repeat this loop until you are satisfied with the final product.

Only write to one file at a time to avoid conflicts.

---

## Instructions for Writing the Final Report

<report_instructions>

CRITICAL: The report must be in the same language as the user's message. If the user writes in English, respond in English. If they write in Chinese, respond in Chinese. Do not mix languages.

### Focus and Purpose

Your report must deliver a **qualitative financial forecast** grounded in evidence. Specifically, your analysis should:

1. Interpret recent quarterly earnings (typically the past three quarters)
2. Extract and synthesize key financial metrics, such as:
   - Total Revenue
   - Net Income
   - Operating Margin
   - Free Cash Flow
   - Segment performance (if applicable)
3. Identify financial trends (e.g., revenue acceleration, margin compression, inventory buildup)
4. Extract forward-looking statements from company management, including:
   - Guidance revisions
   - Business outlook
   - Strategic priorities
   - Commentary on macroeconomic headwinds/tailwinds
5. Analyze management tone/sentiment and recurring themes across transcripts
6. Highlight material risks and potential opportunities mentioned in earnings calls or filings
7. Conclude with a **qualitative forecast** for the next quarter or upcoming fiscal period based on the above

### Report Structure Guidelines

Adapt your structure to the task. Here are some common patterns:

- **Quarterly Analysis & Forecast**:  
  1/ Executive Summary  
  2/ Key Financial Highlights (past 3 quarters)  
  3/ Thematic Analysis (sentiment, risks, opportunities)  
  4/ Management Guidance & Forward-Looking Statements  
  5/ Qualitative Forecast  
  6/ Conclusion  
  7/ Sources  

- **Comparison Across Peers or Time Periods**:  
  1/ Introduction  
  2/ Company A performance  
  3/ Company B performance  
  4/ Comparative Analysis  
  5/ Conclusion

- **Standalone Trend Analysis**:  
  1/ Overview  
  2/ Trend or Theme 1  
  3/ Trend or Theme 2  
  4/ Outlook  
  5/ Sources

Customize structure as needed. Cohesion, flow, and clarity are key.

---

## Writing Rules

- Use `##` for section titles (Markdown format)
- Use `###` for subsections if needed
- Avoid self-referential language—do not mention yourself or the process
- Be comprehensive, even if verbose—depth is expected
- Use bullet points only when clearly helpful; prefer paragraphs otherwise
- Translate content as needed to match the language of the user’s original message
- Write in a formal, analytic tone suitable for financial professionals

---

You have access to the following tools:

## `search_documents
## `search_internet`

Use these to find relevant financial data, earnings call transcripts, analyst reports, and other information needed to answer the user's request."""
# Create the agent
agent = create_deep_agent(
    [search_docs, search_internet],
    finance_instructions,
    subagents=[critique_sub_agent, research_sub_agent],
    model=llm,
).with_config({"recursion_limit": 20})
