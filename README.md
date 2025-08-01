# Agents-for-Finance

Research Agent(s) to perform Qualitative Analysis and construct Financial Forecast Report.

# Approaches

## Single Agent

## Multi-agent (with reflection)
- Planner creates a detailed plan with `to-do` as a list of jsons with a boolean.
- Manager looks at the plan and assigns the worker/research agent with one task at a time (one todo), and tracks progress (chnages the bool values).
- Worker uses tools to search vector DB collections for information and drafts sections.
- Manager puts it all together and throws it to a reviewer for critiqing.
- Criticism goes to manager who can decide to directly go to worker or to planner based on the review.
- Reviewer here can be either another LLM or a human-in-the-loop.

## Google Search + Simple Reflection
- Uses search results as ground truth (less complex RAG)
- Always upto date
- Faster
- Wider range of responses

## Indexed documents + Preset Workflow
- Preset steps, confined to Qualitative Forecasting
- Deep Research (higher token usage, more time, higher calls/min)
- Needs domain expertise
- Relies on indexed data