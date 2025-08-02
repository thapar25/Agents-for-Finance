# Agents for Finance

A research agent designed to perform qualitative analysis on financial documents and generate a structured financial forecast report.

## Project Overview

This project implements an autonomous AI agent capable of synthesizing information from corporate press releases and earnings call transcripts to produce insightful financial forecasts. The agent is served via a FastAPI-based API and leverages a sophisticated architecture for robust and scalable performance.

### Architectural Approach

The system is designed as a microservices-style architecture, orchestrated with Docker Compose:

-   **API Service (FastAPI)**: A Python-based web service (`api`) that exposes the agent's capabilities through a REST API.
-   **Agent Logic (LangGraph)**: The core reasoning engine is built using LangGraph, which orchestrates a ReAct (Reasoning and Acting) loop, allowing the agent to think, select tools, and observe outcomes.
-   **Internal Knowledge (Qdrant)**: Financial documents are chunked, embedded, and stored in a Qdrant vector database (`qdrant`), which serves as the agent's primary knowledge source.
-   **Interaction Logging (MySQL)**: A MySQL database (`mysql`) is used to log all user inputs and agent responses for monitoring, debugging, and future analysis.
-   **Containerization (Docker)**: The entire stack is containerized, ensuring consistent, one-command setup and deployment.

### How the Agent Works

<img width="935" height="623" alt="image" src="https://github.com/user-attachments/assets/c1ba204c-b73c-4c4a-be40-df8a21b46db7" />


The agent follows a chain-of-thought process to fulfill a user's request:
1.  **Understand the Goal**: The agent receives a prompt (e.g., "Generate a forecast for TCS for the next quarter").
2.  **Plan the Steps**: Guided by its master prompt, it formulates a plan. For example: "First, I'll get the key financial metrics from the latest reports. Then, I'll find management's commentary on these numbers from the earnings call transcripts."
3.  **Select & Use Tools**: The agent chooses the best tool for each step. It might use `search_focused` on the `reports` collection for quantitative data, then switch to the `transcripts` collection to get qualitative insights.
4.  **Synthesize & Reflect**: After gathering information, the agent synthesizes the findings. It connects the numbers (e.g., "revenue is up 5%") with the narrative (e.g., "management attributes this to strong demand in the AI sector").
5.  **Generate Structured Output**: Finally, it formats the complete analysis into a structured JSON object, following the `FinancialForecast` Pydantic model, and returns it as the final answer.

## Agent & Tool Design

The agent's behavior is primarily guided by a detailed master prompt and a specialized set of tools.

### Master Prompt

The agent's reasoning is steered by a comprehensive system prompt that defines its persona, analysis framework, and strategy for using tools. This ensures consistent and high-quality output.

```python
# src/agents/utils/prompts.py: detailed_prompt

"""<role>
Senior financial analyst for TCS with expertise in combining quantitative metrics with qualitative management insights.
</role>

<context>
Current fiscal period: Q2_FY2025-26 | Available data: Through Q1_FY2025-26
</context>

<analysis_framework>
Focus on these key areas and their signals:
• **Revenue**: Growth trends, seasonal patterns
• **Operating Margin**: Cost control, inflationary pressures  
• **Profitability**: Net profit/EPS health, investor returns
• **Management Sentiment**: Confidence vs. hedging language
• **Forward Guidance**: Explicit and subtle directional clues
• **Segment Performance**: Winners vs. underperformers
• **Strategic Themes**: Recurring focus areas or persistent risks
</analysis_framework>

<tool_usage_strategy>
**Collection Selection:**
- **Reports Collection** → Financial statements, numerical data, metrics, ratios, quantitative performance
- **Transcripts Collection** → Earnings calls, management commentary, Q&A sessions, qualitative insights

**search_focused**: Filter by specific quarters for targeted analysis
- Reports Collection → Quarter-specific financial metrics, YoY/QoQ comparisons
- Transcripts Collection → Management commentary from specific earnings calls

**search_wide**: Broad search across all available periods
- Reports Collection → Multi-period financial trend analysis  
- Transcripts Collection → Recurring strategic themes, persistent management messages

**search_internet**: External data when internal collections are insufficient
- Real-time stock prices, analyst ratings, competitor benchmarks, market context
</tool_usage_strategy>

<methodology>
1. Extract key financial metrics (Reports DB via search_focused/wide)
2. Pull corresponding management commentary (Transcripts DB)
3. Synthesize numerical trends with qualitative explanations
4. Use internet search only for external validation or real-time data
5. Reflect after each step - do you need additional data points?

Always explain your tool selection reasoning and connect quantitative performance with management narrative.
</methodology>"""
```

### Tools

The agent has access to three asynchronous tools for information retrieval:

-   `search_focused(question: str, collection_name: Collection, quarters: list[Quarters], top_k: int = 4)`
    -   **Description**: The "scalpel." Performs a targeted vector search on the internal knowledge base (`reports` or `transcripts`), filtered by specific fiscal quarters.
    -   **Use Case**: Ideal for fetching precise data, like "What was the operating margin in Q1 FY2024-25?"

-   `search_wide(questions: list[str], collection_name: Collection)`
    -   **Description**: The "net." Performs a broad, multi-query search across an entire collection.
    -   **Use Case**: Best for identifying overarching trends, recurring themes, or strategic shifts over multiple periods. Example query: "What are the most common risks mentioned by management over the last year?"

-   `search_internet(query: str, ...)`
    -   **Description**: The "safety net." Uses the Tavily API to search the internet for external or real-time information.
    -   **Use Case**: Used as a fallback when the internal knowledge base is insufficient, for example, to get the latest stock price, competitor news, or broader market analysis.

## Setup Instructions

Follow these steps to set up and run the project locally.

**Prerequisites:**
-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/thapar25/agents-for-finance.git
cd agents-for-finance
```

### Step 2: Configure Credentials

1.  Create a `.env` file in the project's root directory with the following content:
    ```env
    # .env
    OPENAI_API_KEY="sk-..."
    TAVILY_API_KEY="tvly-..."

    # Optional (if running without Docker)
    DB_USER = 'user'
    DB_PASSWORD = 'password'
    DB_HOST = 'localhost'
    DB_NAME = 'logs_db'

    # Qdrant Configuration
    QDRANT_URL="http://localhost:6333"

    # LangSmith Tracing
    LANGSMITH_TRACING=true
    LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
    LANGSMITH_API_KEY="lsv2_...._"
    LANGSMITH_PROJECT="Agents for Finance"
    
    ```

2.  Open the `.env` file and replace the placeholder values with your actual API keys from [OpenAI](https://platform.openai.com/api-keys) and [Tavily AI](https://app.tavily.com/).

### Step 3: Database Setup (Automated)

The Vector DB (Qdrant) and Logging DB (MySQL) are configured to set themselves up automatically.

-   **Qdrant**: The `docker-compose.yml` is configured to load a pre-built data snapshot (`full-snapshot-....snapshot`) every time it starts, thanks to the `--force-snapshot` flag. **No manual steps are needed.**
-   **MySQL**: Docker Compose automatically starts the container and creates the database. The FastAPI application will create the necessary `logs` table on its first startup.

## How to Run

After cloning the repository and setting up your `.env` file, start the entire application stack with this single command:

```bash
docker-compose up --build
```

Your services are now running:
-   **API Service**: `http://localhost:8000`
-   **API Docs (Swagger UI)**: `http://localhost:8000/docs` (Use this to test the `/api/chat` endpoint)
-   **Qdrant Dashboard**: `http://localhost:6333/dashboard`
-   **MySQL Port**: `3306` (accessible from your local machine)

To stop the services, press `Ctrl+C` in the terminal and then run `docker-compose down`.

## Development & Research

<details>
<summary><b>Possible Agent Approaches (Research Notes)</b></summary>

### Single Agent [✅ Implemented as API]
- One tool to extract financial metrics from Press Releases
- Another tool to extract statements and forward outlook statements from Earning Call transcripts
    - Autonomy : Low
    - No fixed structured output

### Indexed documents + Preset Workflow [WIP]
- Preset steps in a workflow, ensemble retrieval, reflections
    - Controlled Research (higher token usage, more time, higher calls/min)
    - Presets allow well-structured sections and output parsing
    - Needs domain expertise
    - Relies on indexed data
    - Autonomy : Medium

### Multi-agent (with reflection) [WIP]
- Planner creates a detailed plan with `to-do` as a list of jsons with a boolean.
- Manager looks at the plan and assigns the worker/research agent with one task at a time (one todo), and tracks progress (chnages the bool values).
- Worker uses tools to search vector DB collections for information and drafts sections.
- Manager puts it all together and throws it to a reviewer for critiqing.
- Criticism goes to manager who can decide to directly go to worker or to planner based on the review.
- Reviewer here can be either another LLM or a human-in-the-loop.
    - Context Isolation
    - Read [deep agents](https://blog.langchain.com/deep-agents/) implementation inspired by [article](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html)
    - Autonomy : High

### Google Search + Simple Reflection
- Single tool -> Google Search
    - Uses search results as ground truth (less complex RAG)
    - Always upto date
    - Faster
    - Wider range of responses
    - Autonomy : High

</details>
