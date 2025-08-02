# Agents-for-Finance

Research Agent(s) to perform Qualitative Analysis and construct Financial Forecast Report.

## Current Implementation

### Solution 1: General Tool Calling Agent

`route: POST /chat`

### Solution 2: RAG Workflow

`route: POST /forecast`





# Possible Approaches

<details>

<summary>A brief breakdown of all possible approaches</summary>

## Single Agent [✅ Implemented as API]
- One tool to extract financial metrics from Press Releases
- Another tool to extract statements and forward outlook statements from Earning Call transcripts
    - Autonomy : Low
    - No fixed structured output


## Indexed documents + Preset Workflow [✅ Implemented as API]
- Preset steps in a workflow, ensemble retrieval, reflections
    - Controlled Research (higher token usage, more time, higher calls/min)
    - Presets allow well-structured sections and output parsing
    - Needs domain expertise
    - Relies on indexed data
    - Autonomy : Medium



## Multi-agent (with reflection)
- Planner creates a detailed plan with `to-do` as a list of jsons with a boolean.
- Manager looks at the plan and assigns the worker/research agent with one task at a time (one todo), and tracks progress (chnages the bool values).
- Worker uses tools to search vector DB collections for information and drafts sections.
- Manager puts it all together and throws it to a reviewer for critiqing.
- Criticism goes to manager who can decide to directly go to worker or to planner based on the review.
- Reviewer here can be either another LLM or a human-in-the-loop.
    
    - Context Isolation
    - Read [deep agents](https://blog.langchain.com/deep-agents/) implementation inspired by [article](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html)
    - Autonomy : High


## Google Search + Simple Reflection
- Single tool -> Google Search
    - Uses search results as ground truth (less complex RAG)
    - Always upto date
    - Faster
    - Wider range of responses
    - Autonomy : High

</details>